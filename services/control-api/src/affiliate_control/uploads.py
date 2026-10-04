"""Bounded owner MP4 intake, full decode and optimistic workspace attachment."""
import hashlib
import json
import re
import subprocess
import threading
import uuid

from affiliate_domain.two_video import invalidate, stamp
from .content_commands import find

MAX_BYTES = 100 * 1024 * 1024
LOCK = threading.Lock()


def metadata(handler):
    headers = handler.headers
    if headers.get("Content-Type") != "video/mp4" or headers.get("Transfer-Encoding"):
        raise ValueError("Chỉ nhận tệp MP4 trực tiếp, tối đa 100 MB.")
    size = int(headers.get("Content-Length", 0))
    if not 16 <= size <= MAX_BYTES:
        raise ValueError("Tệp phải từ 16 byte đến 100 MB.")
    target = headers.get("X-Media-Target")
    ident = headers.get("X-Media-Id", "")
    if target not in ("source", "selected") or not re.fullmatch(r"[a-f0-9-]{36}", ident):
        raise ValueError("Đích tệp không hợp lệ.")
    return size, target, ident, int(headers.get("X-Workspace-Version", "0"))


def inspect(runtime, file, folder):
    script = runtime / "upgrade/inspect_video.swift" if runtime else None
    if not script or not script.is_file():
        raise ValueError("Bộ kiểm MP4 trên máy chưa khả dụng; chưa nhận tệp vào thư viện.")
    qc = folder / "inspection"
    qc.mkdir()
    result = subprocess.run(["/usr/bin/swift", str(script), str(file), str(qc)],
                            capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise ValueError("MP4 không giải mã đầy đủ; không đưa vào hàng chờ.")
    data = json.loads(result.stdout)
    if (data.get("full_decode_passed") is not True or not 0 < data["duration_seconds"] <= 180
            or not 240 <= data["display_width"] <= 3840 or not 240 <= data["display_height"] <= 3840):
        raise ValueError("Video cần dài tối đa 180 giây và kích thước từ 240 đến 3840 pixel.")
    return {"sha256": data["sha256"], "duration_seconds": data["duration_seconds"],
            "width": data["display_width"], "height": data["display_height"], "technical_passed": True,
            "perceptual_reviewed": False, "origin": "owner_uploaded_not_flow_verified", "observed_at": stamp()}


def attach(state, target, ident, artifact):
    if target == "source":
        source = find(state["sources"], ident)
        source["asset"] = artifact
        for batch in state["batches"]:
            branch = batch["branches"]["selected"]
            if branch["source_id"] == ident:
                invalidate(branch)
        return {"source_id": ident}
    batch = find(state["batches"], ident)
    branch = batch["branches"]["selected"]
    source = find(state["sources"], branch["source_id"])
    confirm = branch.get("confirmation")
    if (not source.get("asset") or not confirm or confirm.get("asset_hash") != source["asset"]["sha256"]
            or confirm["expires_at"] <= stamp()):
        raise ValueError("Cần tệp nguồn và xác nhận đúng mã băm trước khi nhận bản xử lý.")
    if branch["status"] == "processing":
        raise ValueError("Nhánh đang xử lý; chờ xong trước khi nhận bản.")
    if branch.get("artifact"):
        invalidate(branch)
        branch["confirmation"] = confirm
    branch.update(status="ready", artifact=artifact, completed_at=stamp(),
                  notes=["Đã nhận bản xử lý từ chủ · kiểm kỹ thuật đạt; xem trước/sau và duyệt chất lượng."])
    return {"batch_id": ident, "kind": "selected", "revision": branch["revision"]}


def receive(handler):
    size, target, ident, version = metadata(handler)
    app = handler.server.app
    if not LOCK.acquire(blocking=False):
        raise ValueError("Đang nhận/kiểm một tệp khác; thử sau khi hoàn tất.")
    folder = None
    try:
        state = app.content.store.read()
        find(state["sources" if target == "source" else "batches"], ident)
        if state["version"] != version:
            from .store import BusyError
            raise BusyError("Workspace đã đổi; đọc lại trước khi gửi tệp.")
        folder = app.settings.state / "media" / str(uuid.uuid4())
        folder.mkdir(mode=0o700, parents=True)
        file, remaining, digest = folder / "video.mp4", size, hashlib.sha256()
        handler.connection.settimeout(60)
        with file.open("xb") as stream:
            while remaining:
                chunk = handler.rfile.read(min(65536, remaining))
                if not chunk:
                    raise ValueError("Tệp gửi chưa đầy đủ.")
                stream.write(chunk); digest.update(chunk); remaining -= len(chunk)
        with file.open("rb") as stream:
            is_mp4 = stream.read(16)[4:8] == b"ftyp"
        if not is_mp4:
            raise ValueError("Tệp không có cấu trúc MP4.")
        artifact = inspect(app.settings.runtime, file, folder)
        if artifact["sha256"] != digest.hexdigest():
            raise ValueError("Mã băm tệp không khớp.")
        artifact["relative_path"] = str(file.relative_to(app.settings.state))
        body = {"expected_version": version, "idempotency_key": str(uuid.uuid4()),
                "target": target, "ident": ident, "sha256": artifact["sha256"]}
        result, _ = app.content.store.command(body, lambda current: attach(current, target, ident, artifact))
        return result
    finally:
        LOCK.release()
        # Failed/abandoned files remain private for diagnosis, never considered ready or served by ID.
