"""Workspace mutations; browser data cannot select a command or file path to execute."""
from copy import deepcopy
from datetime import datetime, timezone
import uuid

from affiliate_domain.two_video import BRANCHES, confirm_source, invalidate, new_batch, select_source, source_url, stamp, text
from .content_initial import initialize_branch
from .content_edits import EDITORS


def find(items, ident):
    result = next((item for item in items if item["id"] == ident), None)
    if result is None:
        raise ValueError("Không tìm thấy đối tượng.")
    return result


def add_source(state, data):
    from affiliate_domain.source_links import provider
    product = find(state["products"], data["product_id"])
    url = source_url(data["url"])
    prior = next((s for s in state["sources"] if s["url"] == url and s["product_id"] == product["id"]), None)
    if prior:
        return prior
    if len(state["sources"]) >= 200:
        raise ValueError("Danh sách đã đủ 200 nguồn; cần quản lý danh mục trước khi thêm.")
    source = {"id": str(uuid.uuid4()), "product_id": product["id"], "url": url,
              "title": text(data["title"], 180), "creator": text(data.get("creator", "Chưa biết"), 120),
              "method": data.get("method", "owner_entry_not_provider_verified"), "observed_at": stamp(),
              "published_at": data.get("published_at"), "query": data.get("query", state["settings"]["query"]),
              "views": None, "hook_score": None, "rights": "awaiting_owner", "provider": provider(url)}
    state["sources"].append(source)
    return source


def batch_command(state, body, capabilities):
    from affiliate_domain.two_video import process_blockers
    action, data = body["action"], body.get("data", {})
    batch = find(state["batches"], body["batch_id"])
    kind = body.get("kind", "selected")
    if kind not in BRANCHES:
        raise ValueError("Sai nhánh video.")
    branch = batch["branches"][kind]
    if action == "select":
        if kind != "selected":
            raise ValueError("Chỉ video thứ hai dùng danh sách nguồn.")
        select_source(batch, find(state["sources"], data["source_id"]))
        reuse_confirmation(state, branch)
    elif action == "confirm":
        if kind != "selected":
            raise ValueError("Nhánh tự tạo không dùng xác nhận video nguồn.")
        confirm_source(branch, find(state["sources"], branch["source_id"]), data)
    elif action in ("hold", "unhold"):
        branch["hold"] = action == "hold"
    elif action == "revise":
        invalidate(branch)
    elif action in EDITORS:
        EDITORS[action](branch, data)
    elif action == "process":
        if find(state["products"], batch["product"]["id"]).get("status") == "skipped":
            raise ValueError("Sản phẩm đang bỏ qua; khôi phục trước khi xử lý.")
        reasons = process_blockers(branch, capabilities)
        if reasons:
            raise ValueError(" · ".join(reasons))
        if any(b["branches"]["created"]["status"] == "processing" for b in state["batches"]):
            raise ValueError("Một video đang dựng; chờ xong trước khi chạy thêm.")
        branch.update(status="processing", run_id=str(uuid.uuid4()), notes=["Đã nhận yêu cầu dựng"], started_at=stamp())
    else:
        raise ValueError("Hành động chưa hỗ trợ.")
    return {"batch_id": batch["id"], "kind": kind, "revision": branch["revision"], "run_id": branch["run_id"]}


def reuse_confirmation(state, branch):
    if state["settings"]["confirmation_mode"] != "reuse_valid":
        return
    source = find(state["sources"], branch["source_id"])
    asset_hash = source.get("asset", {}).get("sha256")
    for batch in reversed(state["batches"]):
        prior = batch["branches"]["selected"]
        confirmation = prior.get("confirmation")
        valid = confirmation and datetime.fromisoformat(confirmation["expires_at"]) > datetime.now(timezone.utc)
        if (prior["source_id"] == branch["source_id"] and valid and confirmation.get("url") == source["url"]
                and confirmation.get("asset_hash") == asset_hash):
            branch["confirmation"] = deepcopy(prior["confirmation"])
            break


def mutate(state, body, capabilities):
    action, data = body["action"], body.get("data", {})
    from .catalog_commands import COMMANDS
    from .report_commands import save, post_control
    if action == "affiliate_report":
        return save(state, data)
    if action == "post_control":
        return post_control(state, data)
    if action in COMMANDS:
        return COMMANDS[action](state, data)
    if action == "settings":
        query = text(data["query"], 250)
        if (data.get("order") not in ("relevance", "date", "viewCount") or type(data.get("limit")) is not int
                or not 1 <= data["limit"] <= 25 or data.get("confirmation_mode") not in ("per_source", "reuse_valid")):
            raise ValueError("Cấu hình tìm kiếm không hợp lệ.")
        state["settings"].update(query=query, order=data["order"], limit=data["limit"], confirmation_mode=data["confirmation_mode"])
        return {"saved": True}
    if action == "source":
        return {"source_id": add_source(state, data)["id"]}
    if action == "batch":
        if len(state["batches"]) >= 100:
            raise ValueError("Đã đủ 100 batch; cần lưu trữ lịch sử trước khi tạo thêm.")
        product = find(state["products"], data["product_id"])
        if product.get("status") == "skipped":
            raise ValueError("Sản phẩm đang bỏ qua; khôi phục trước khi làm video.")
        profile = state["settings"] | {"query": product.get("query") or state["settings"]["query"]}
        batch = new_batch(product, profile)
        initialize_branch(batch)
        state["batches"].append(batch)
        return {"batch_id": batch["id"]}
    return batch_command(state, body, capabilities)
