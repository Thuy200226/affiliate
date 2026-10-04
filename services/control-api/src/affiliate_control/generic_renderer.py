"""Offline generic graphics/voice, compiled from repository-owned fixed native sources."""
import hashlib
from pathlib import Path
import threading

LOCK = threading.Lock()


def binary(root, work, command):
    native = Path(__file__).resolve().parents[2] / "native"
    sources = [native / ("product_" + name + ".swift") for name in ("drawing", "mux", "renderer")]
    digest = hashlib.sha256(b"".join(s.read_bytes() for s in sources)).hexdigest()[:16]
    folder = root / "native"
    folder.mkdir(mode=0o700, exist_ok=True)
    output = folder / ("product-" + digest)
    with LOCK:
        if not output.exists():
            command(["/usr/bin/swiftc", *map(str, sources), "-o", str(output)], work, "build-generic", 90)
            output.chmod(0o700)
    return output


def render(root, work, manifest, output, command):
    command([str(binary(root, work, command)), str(manifest), str(output)], work, "render-generic", 300)
