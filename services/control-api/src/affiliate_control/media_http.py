"""Session-protected Range preview, resolved from stored artifact IDs only."""
import re


def serve(handler):
    source = re.fullmatch(r"/api/content/source-media/([a-f0-9-]{36})", handler.path)
    if source:
        app = handler.server.app
        item = next((s for s in app.content.store.read()["sources"] if s["id"] == source[1]), None)
        return send(handler, item.get("asset") if item else None)
    match = re.fullmatch(r"/api/content/media/([a-f0-9-]{36})/(created|selected)/([0-9]+)", handler.path)
    if not match:
        return False
    batch_id, kind, revision = match.groups()
    app = handler.server.app
    state = app.content.store.read()
    batch = next((b for b in state["batches"] if b["id"] == batch_id), None)
    branch = batch["branches"][kind] if batch else None
    candidates = [branch] + branch.get("history", []) if branch else []
    version = next((b for b in candidates if b["revision"] == int(revision) and b.get("artifact")), None)
    if not version:
        handler.reply(404, {"error": "Không có bản video này."})
        return True
    return send(handler, version["artifact"])


def send(handler, artifact):
    if not artifact:
        handler.reply(404, {"error": "Chưa nhận tệp nguồn."})
        return True
    root = handler.server.app.settings.state.resolve()
    file = (root / artifact["relative_path"]).resolve()
    if not file.is_relative_to(root / "media") or not file.is_file():
        handler.reply(404, {"error": "Tệp video chưa khả dụng."})
        return True
    size, start = file.stat().st_size, 0
    end = size - 1
    ranges = handler.headers.get("Range")
    if ranges:
        part = re.fullmatch(r"bytes=([0-9]+)-([0-9]*)", ranges)
        if not part or int(part[1]) >= size:
            handler.reply(416, {"error": "Khoảng video không hợp lệ."})
            return True
        start, end = int(part[1]), min(int(part[2]) if part[2] else size - 1, size - 1)
        if end < start:
            handler.reply(416, {"error": "Khoảng video không hợp lệ."})
            return True
    from .security import HEADERS
    handler.send_response(206 if ranges else 200)
    for key, value in HEADERS.items():
        handler.send_header(key, value)
    handler.send_header("Content-Type", "video/mp4")
    handler.send_header("Accept-Ranges", "bytes")
    handler.send_header("Content-Length", str(end - start + 1))
    if ranges:
        handler.send_header("Content-Range", f"bytes {start}-{end}/{size}")
    handler.end_headers()
    write_range(handler, file, start, end)
    return True


def write_range(handler, file, start, end):
    with file.open("rb") as stream:
        stream.seek(start)
        remaining = end - start + 1
        while remaining:
            chunk = stream.read(min(65536, remaining))
            if not chunk:
                break
            try:
                handler.wfile.write(chunk)
            except (BrokenPipeError, ConnectionResetError):
                return  # Seeking/closing the preview cancels the old request normally.
            remaining -= len(chunk)
