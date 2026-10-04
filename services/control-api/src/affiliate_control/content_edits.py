"""Validated, revision-aware edits kept separate from queue mutations."""
import re

from affiliate_domain.two_video import invalidate, text


def edit_copy(branch, data):
    tags = text(data.get("hashtags", ""), 250, minimum=0).split()
    if len(tags) > 5 or any(not re.fullmatch(r"#[\w]{1,40}", tag) for tag in tags):
        raise ValueError("Tối đa 5 hashtag đúng dạng #chủđề.")
    if branch["status"] == "processing":
        raise ValueError("Chờ dựng xong hoặc tạo revision trước khi sửa nội dung đăng.")
    branch["copy"] = {"title": text(data["title"], 95), "description": text(data["description"], 4000),
                      "hashtags": list(dict.fromkeys(tags))}
    branch["copy_version"] = branch.get("copy_version", 1) + 1
    if branch.get("artifact"):
        branch["artifact"]["perceptual_reviewed"] = False


def edit_script(branch, data):
    if branch["kind"] != "created" or not isinstance(data.get("scenes"), list) or len(data["scenes"]) != 5:
        raise ValueError("Cần 5 cảnh cho video tự tạo.")
    scenes = [{"kind": old["kind"], "headline": text(new["headline"], 50),
               "label": text(new["label"], 40), "voice": text(new["voice"], 180)}
              for old, new in zip(branch["scenes"], data["scenes"])]
    invalidate(branch)
    branch["scenes"] = scenes


def edit_request(branch, data):
    if branch["kind"] != "selected":
        raise ValueError("Chỉnh nguồn thuộc video thứ hai.")
    request = text(data["request"], 700)
    invalidate(branch)
    branch["edit_request"] = request


def review(branch, data):
    artifact = branch.get("artifact")
    if not artifact or data.get("sha256") != artifact["sha256"] or data.get("watched_listened") is not True:
        raise ValueError("Cần xem/nghe đúng tệp trước khi duyệt chất lượng.")
    artifact.update(perceptual_reviewed=True, reviewed_copy_version=branch.get("copy_version", 1))


EDITORS = {"copy": edit_copy, "script": edit_script, "edit": edit_request, "review": review}


def validate_body(body):
    schemas = {"settings": {"query", "order", "limit", "confirmation_mode"},
               "source": {"product_id", "url", "title", "creator"}, "batch": {"product_id"},
               "search": {"product_id"}, "select": {"source_id"}, "confirm": {"media_audio", "person_edit"},
               "hold": set(), "unhold": set(), "revise": set(), "process": set(),
               "copy": {"title", "description", "hashtags"}, "script": {"scenes"},
               "review": {"sha256", "watched_listened"}, "edit": {"request"}}
    fields = schemas.get(body.get("action"))
    if fields is None or set(body.get("data", {})) - fields:
        raise ValueError("Hành động hoặc trường dữ liệu chưa hỗ trợ.")
