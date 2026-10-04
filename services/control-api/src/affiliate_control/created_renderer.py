"""Use the owner's existing offline voice/graphics tools, never modify legacy jobs."""
import hashlib
import json
from pathlib import Path
import subprocess


def available(runtime):
    names = ("render_local_affiliate_v3", "preflight_local_video.swift", "local_neural_voice.py",
             "render_flow_hybrid_preview.swift", "inspect_video.swift", ".venv-voice/bin/python")
    return runtime is not None and all((runtime / "upgrade" / name).is_file() for name in names)


def scene_plan(product):
    if (product.get("shop_id"), product.get("item_id")) != ("928446709", "24035184620"):
        raise ValueError("Bộ dựng hiện tại chỉ có hình M31; không dùng hình sai cho sản phẩm khác.")
    rows = [
        ("hook", "QUAY MỘT MÌNH\nHAY CÙNG BẠN?", "CHỌN THEO CÁCH BẠN QUAY", "Quay clip một mình, hay quay cùng bạn? Chọn bộ micro theo cách bạn quay."),
        ("product", "MICRO CÀI ÁO M31", "CHO ĐIỆN THOẠI", "M31 là micro cài áo cho điện thoại. Cài micro lên áo để bố trí bộ quay gọn gàng."),
        ("options", "MỘT HAY HAI\nMICRO?", "CHỌN ĐÚNG BỘ", "Bạn quay một người hay hai người? Xem bộ một hoặc hai micro trước khi chọn."),
        ("case", "CHỌN ĐÚNG\nĐẦU CẮM", "THEO ĐIỆN THOẠI CỦA BẠN", "Nhớ chọn đầu cắm phù hợp với chiếc điện thoại bạn đang sử dụng."),
        ("ending", "XEM BỘ M31", "LINK MICRO M31 TRÊN HỒ SƠ", "Chạm tên kênh, mở link Micro M31 trên hồ sơ để xem đúng bộ sản phẩm."),
    ]
    return [dict(zip(("kind", "headline", "label", "voice"), row)) for row in rows]


def command(args, work, name, timeout):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, shell=False)
    (work / (name + ".log")).write_text(result.stdout + result.stderr)
    if result.returncode:
        raise ValueError("Bước " + name + " chưa đạt; xem nhật ký cục bộ.")
    return result


def render(runtime, root, batch, branch, progress):
    if not available(runtime):
        raise ValueError("Thiếu công cụ dựng cục bộ.")
    work = root / "media" / branch["run_id"]
    work.mkdir(parents=True, exist_ok=False, mode=0o700)
    from .generic_plan import scenes as generic_scenes
    known_m31 = (batch["product"].get("shop_id"), batch["product"].get("item_id")) == ("928446709", "24035184620")
    default_scenes = scene_plan(batch["product"]) if known_m31 else generic_scenes(batch["product"])
    scenes = branch.get("scenes") or default_scenes
    manifest = work / "manifest.json"
    manifest.write_text(json.dumps({"job_id": batch["id"], "scenes": scenes}, ensure_ascii=False))
    tools = runtime / "upgrade"
    progress("Kiểm bố cục và chuẩn bị giọng")
    if known_m31:
        command(["/usr/bin/swift", str(tools / "preflight_local_video.swift"), str(manifest)], work, "preflight", 60)
    else:
        from .generic_renderer import binary
        command([str(binary(root, work, command)), str(manifest), "--check"], work, "preflight-generic", 60)
    progress("Đang tạo giọng Trúc Ly trên máy")
    command([str(tools / ".venv-voice/bin/python"), str(tools / "local_neural_voice.py"),
             str(manifest), str(work), "--voice", "Trúc Ly"], work, "voice", 300)
    for i, scene in enumerate(scenes):
        scene["audio_file"] = str(work / f"speech-{i}.wav")
    manifest.write_text(json.dumps({"job_id": batch["id"], "scenes": scenes}, ensure_ascii=False))
    progress("Đang dựng chuyển động, giọng và chữ")
    base, output = work / "base.mp4", work / "video.mp4"
    if known_m31:
        command([str(tools / "render_local_affiliate_v3"), str(manifest), str(work), str(base)], work, "render", 300)
        command(["/usr/bin/swift", str(tools / "render_flow_hybrid_preview.swift"), str(base), "-", str(output)], work, "compose", 180)
    else:
        from .generic_renderer import render as generic_render
        generic_render(root, work, manifest, output, command)
    progress("Giải mã toàn bộ và kiểm tra âm thanh")
    inspection = work / "inspection"
    inspection.mkdir()
    result = command(["/usr/bin/swift", str(tools / "inspect_video.swift"), str(output), str(inspection)], work, "inspection", 180)
    quality = json.loads(result.stdout)
    if not (quality.get("full_decode_passed") is True and quality.get("display_width") == 1080
            and quality.get("display_height") == 1920 and quality.get("audio_samples", 0) > 0
            and quality.get("clipped_sample_fraction", 1) < 0.001
            and 15 <= quality.get("duration_seconds", 0) <= 45):
        raise ValueError("Video chưa đạt kiểm tra kỹ thuật.")
    return {"relative_path": str(output.relative_to(root)), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "duration_seconds": quality["duration_seconds"], "width": 1080, "height": 1920,
            "technical_passed": True, "perceptual_reviewed": False, "paid_AI_API_calls": 0}
