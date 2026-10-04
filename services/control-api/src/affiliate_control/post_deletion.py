"""Separate irreversible owner action. Reserve before DELETE, never blind retry."""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from affiliate_domain.two_video import stamp


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_):
        return None


def call(token, route, query, method="GET"):
    url = "https://www.googleapis.com/youtube/v3/" + route + "?" + urlencode(query)
    request = Request(url, headers={"Authorization": "Bearer " + token}, method=method)
    try:
        with build_opener(NoRedirect()).open(request, timeout=15) as response:
            if method == "DELETE":
                return response.status == 204
            raw = response.read(500_001)
            if len(raw) > 500_000:
                raise ValueError("Kết quả kiểm quyền vượt giới hạn.")
            data = json.loads(raw)
            if not isinstance(data, dict) or not isinstance(data.get("items"), list):
                raise ValueError("Kết quả kiểm quyền chưa hợp lệ.")
            return data
    except HTTPError:
        raise ValueError("YouTube từ chối; kiểm OAuth/quyền sở hữu, không lưu token vào log.") from None
    except URLError:
        raise TimeoutError("Không xác định kết quả YouTube; đối chiếu trước khi thử lại.") from None


def ownership(token, ident, accounts):
    channels = call(token, "channels", {"part": "snippet", "mine": "true"}).get("items", [])
    channels = [c for c in channels if c.get("snippet", {}).get("customUrl", "").lower() in accounts]
    video = call(token, "videos", {"part": "snippet", "id": ident}).get("items", [])
    if len(channels) != 1 or len(video) != 1 or video[0].get("snippet", {}).get("channelId") != channels[0].get("id"):
        raise ValueError("OAuth/tài khoản/video không khớp; không xoá.")
    return channels[0]["id"]


def delete(app, body):
    allowed = {"video_id", "confirm_id", "permanent", "expected_version", "idempotency_key"}
    if set(body) != allowed or body["permanent"] is not True or body["confirm_id"] != body["video_id"]:
        raise ValueError("Cần xác nhận xoá vĩnh viễn đúng video ID.")
    state = app.content.store.read()
    ident = body["video_id"]
    registry = app.bridge.snapshot("artifacts/current-published-videos.json").get("videos", [])
    if ident not in {v.get("video_id") for v in registry}:
        raise ValueError("Video không có trong registry hiện tại.")
    previous = app.content.store.prior_command(body)
    if previous:
        return previous | {"message": "Đã nhận yêu cầu này; xem trạng thái, không gửi xoá lần hai."}
    controls = state.get("publication_controls", {})
    if controls.get(ident, {}).get("deletion") in ("deleting", "uncertain", "deleted_on_youtube"):
        raise ValueError("Đã có thao tác xoá; cần đối chiếu trạng thái trước.")
    token = app.connections.secret("read", "youtube")
    channel = ownership(token, ident, {p["account"].lower() for p in state["products"]})
    def reserve(current):
        if current["publication_controls"].get(ident, {}).get("deletion") in ("deleting", "uncertain", "deleted_on_youtube"):
            raise ValueError("Một yêu cầu xoá khác đã được nhận; không gửi trùng.")
        current["publication_controls"].setdefault(ident, {}).update(deletion="deleting", deletion_at=stamp(), channel_id=channel)
        return {"video_id": ident, "reserved": True}
    result, created = app.content.store.command(body, reserve)
    if not created:
        return result
    try:
        ok = call(token, "videos", {"id": ident}, "DELETE")
        status = "deleted_on_youtube" if ok else "uncertain"
    except (ValueError, TimeoutError, OSError):
        status = "uncertain"
    def finish(current):
        current["publication_controls"][ident].update(deletion=status, deletion_at=stamp())
        return {"video_id": ident, "deletion": status}
    return app.content.store.system_update(finish)
