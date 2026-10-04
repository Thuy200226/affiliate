from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class Settings:
    runtime: Path | None = None
    state: Path = REPO / ".local"
    web: Path = REPO / "apps/console"
    port: int = 8787
    bind: str = "127.0.0.1"

    def __post_init__(self):
        if self.bind not in ("127.0.0.1", "0.0.0.0") or not 1024 <= self.port <= 65535:
            raise ValueError("Unsupported bind/port")
        if self.runtime is not None:
            expected = self.runtime / "upgrade/run_existing_affiliate_flow.py"
            if not self.runtime.is_absolute() or not expected.is_file():
                raise ValueError("Runtime does not contain the expected legacy runner")

    @property
    def hosts(self):
        return {f"127.0.0.1:{self.port}", f"localhost:{self.port}"}
