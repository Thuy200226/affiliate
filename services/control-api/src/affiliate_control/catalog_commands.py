"""Catalog edits preserve batch snapshots and previously published artifacts."""
from affiliate_domain.catalog import binding_status, validate_product, verify_binding
from affiliate_domain.two_video import stamp


def product(state, ident):
    result = next((p for p in state["products"] if p["id"] == ident), None)
    if not result:
        raise ValueError("Không tìm thấy sản phẩm.")
    return result


def save(state, data):
    new = validate_product(data)
    if any(p["id"] != new["id"] and (p["shop_id"], p["item_id"], p["variant"], p["account"], p["platform"]) ==
           (new["shop_id"], new["item_id"], new["variant"], new["account"], new["platform"]) for p in state["products"]):
        raise ValueError("Sản phẩm/biến thể cho tài khoản này đã có; hãy sửa bản hiện có.")
    if data.get("product_id"):
        old = product(state, new["id"])
        new.update(priority=old.get("priority", "normal"), status=old.get("status", "active"))
        if all(old.get(k) == new.get(k) for k in ("affiliate_url", "shop_id", "item_id", "variant", "account", "platform", "placement")):
            new["link_evidence"] = old.get("link_evidence")
        old.clear(); old.update(new)
    else:
        if len(state["products"]) >= 200:
            raise ValueError("Đã đủ 200 sản phẩm; lưu trữ danh mục trước khi thêm.")
        state["products"].append(new)
    return {"product_id": new["id"]}


def choice(state, data):
    item = product(state, data["product_id"])
    if data.get("choice") not in ("first", "normal", "skip", "restore"):
        raise ValueError("Chọn Làm trước, Bình thường, Bỏ qua hoặc Khôi phục.")
    item.update(updated_at=stamp())
    if data["choice"] in ("skip", "restore"):
        item["status"] = "skipped" if data["choice"] == "skip" else "active"
        if data["choice"] == "skip":
            for batch in state["batches"]:
                if batch["product"]["id"] == item["id"]:
                    for branch in batch["branches"].values():
                        branch["hold"] = True
    else:
        item["priority"] = data["choice"]
    return {"product_id": item["id"], "status": item["status"], "priority": item["priority"]}


def verify(state, data):
    item = product(state, data["product_id"])
    item["link_evidence"] = verify_binding(item, data)
    item["link_status"] = binding_status(item)
    return {"product_id": item["id"], "link_status": item["link_status"]}


COMMANDS = {"product": save, "product_choice": choice, "link_verify": verify}
