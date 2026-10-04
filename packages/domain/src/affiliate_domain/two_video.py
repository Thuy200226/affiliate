"""Two independent outputs; choosing a source must not invalidate the created video."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import re
from urllib.parse import parse_qs, urlsplit
import uuid

BRANCHES = ("created", "selected")


def stamp():
    return datetime.now(timezone.utc).isoformat()


def text(value, limit, minimum=1):
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= limit:
        raise ValueError("Văn bản trống hoặc vượt giới hạn.")
    if any(ord(c) < 32 and c not in "\n\t" for c in value):
        raise ValueError("Văn bản có ký tự không hợp lệ.")
    return value.strip()


def source_url(value):
    parsed = urlsplit(text(value, 500))
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError("Cần URL video HTTPS hợp lệ.")
    host = parsed.hostname
    if host in ("www.youtube.com", "youtube.com", "youtu.be"):
        ident = (parsed.path.lstrip("/") if host == "youtu.be" else
                 parsed.path.split("/")[2] if parsed.path.startswith("/shorts/") else
                 parse_qs(parsed.query).get("v", [""])[0])
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", ident):
            return "https://www.youtube.com/watch?v=" + ident
    if host in ("www.tiktok.com", "tiktok.com") and re.fullmatch(r"/@[^/]+/video/[0-9]+/?", parsed.path):
        return "https://www.tiktok.com" + parsed.path.rstrip("/")
    if host in ("www.instagram.com", "instagram.com") and re.fullmatch(r"/(?:reel|p)/[A-Za-z0-9_-]+/?", parsed.path):
        return "https://www.instagram.com" + parsed.path.rstrip("/") + "/"
    raise ValueError("Chỉ nhận URL video YouTube, TikTok hoặc Instagram.")


def new_batch(product, profile):
    if not product.get("id") or not product.get("title"):
        raise ValueError("Chưa cấu hình sản phẩm.")
    branches = {}
    for kind in BRANCHES:
        branches[kind] = {"kind": kind, "revision": 1, "status": "draft", "hold": False,
                          "source_id": None, "confirmation": None, "run_id": None,
                          "artifact": None, "notes": [], "history": [], "copy": {
                              "title": product["title"], "description": product.get("summary", ""),
                              "hashtags": ["#MicroM31"] if product.get("item_id") == "24035184620" else []}}
    return {"id": str(uuid.uuid4()), "created_at": stamp(), "product": deepcopy(product),
            "profile": deepcopy(profile), "branches": branches}


def invalidate(branch):
    previous = deepcopy({key: value for key, value in branch.items() if key != "history"})
    branch.setdefault("history", []).append(previous)
    branch["history"] = branch["history"][-20:]
    branch.update(revision=branch["revision"] + 1, status="draft", run_id=None,
                  artifact=None, confirmation=None, notes=[])


def select_source(batch, source):
    if source["product_id"] != batch["product"]["id"]:
        raise ValueError("Video thuộc sản phẩm khác.")
    branch = batch["branches"]["selected"]
    if branch.get("source_id") != source["id"]:
        invalidate(branch)
        branch["source_id"] = source["id"]


def confirm_source(branch, source, body):
    if branch.get("source_id") != source["id"]:
        raise ValueError("Nguồn đã thay đổi; chọn lại trước khi xác nhận.")
    if body.get("media_audio") is not True:
        raise ValueError("Chủ cần xác nhận nguồn media/âm thanh.")
    branch["confirmation"] = {"source_id": source["id"], "url": source["url"],
                              "media_audio": True, "person_edit": body.get("person_edit") is True,
                              "confirmed_at": stamp(), "by": "local_owner", "asset_hash": None,
                              "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()}


def process_blockers(branch, capabilities):
    if branch["hold"]:
        return ["Bạn đang giữ bản này; bỏ giữ trước khi xử lý."]
    if branch["status"] == "processing":
        return ["Bản này đang xử lý."]
    if branch["status"] != "draft":
        return ["Tạo revision làm lại trước khi dựng thêm, không ghi đè bản đã có."]
    if branch["kind"] == "created":
        return [] if capabilities.get("created_renderer") else ["Bộ dựng cục bộ chưa khả dụng."]
    reasons = []
    if not branch.get("source_id"):
        reasons.append("Chọn một video trong danh sách nguồn.")
    elif not branch.get("confirmation"):
        reasons.append("Chủ chưa xác nhận nguồn đã chọn.")
    confirmation = branch.get("confirmation")
    if confirmation and (confirmation.get("source_id") != branch["source_id"] or
            datetime.fromisoformat(confirmation["expires_at"]) <= datetime.now(timezone.utc)):
        reasons.append("Xác nhận nguồn đã hết hạn hoặc không khớp lựa chọn.")
    reasons.append("Chưa có runner Flow lấy/chỉnh MP4 nguồn; không giả video tự tạo thành video nguồn.")
    return reasons
