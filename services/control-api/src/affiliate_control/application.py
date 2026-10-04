import subprocess
import threading

from .legacy import ACTIONS, Legacy
from .overview import summarize
from .security import Sessions
from .store import Store
from .content import Content


class UnavailableError(ValueError):
    pass


class Application:
    def __init__(self, settings, bridge=None):
        self.settings = settings
        settings.state.mkdir(parents=True, exist_ok=True, mode=0o700)
        (settings.state / "logs").mkdir(exist_ok=True, mode=0o700)
        self.sessions = Sessions(settings.state)
        self.store = Store(settings.state / "runs.sqlite")
        self.bridge = bridge or Legacy(settings)
        self.content = Content(settings)

    def overview(self):
        return summarize(self.bridge)

    def start(self, flow, body):
        if flow not in ACTIONS or not isinstance(body, dict) or set(body) != {"idempotency_key"}:
            raise ValueError("Invalid action/body")
        # A retry of a completed request still resolves when the queue changes.
        previous = self.store.find(flow, body["idempotency_key"])
        if previous:
            return previous
        enabled, reason = self.bridge.eligible(flow)
        if not enabled:
            raise UnavailableError(reason)
        run, created = self.store.reserve(flow, body["idempotency_key"])
        if created:
            threading.Thread(target=self.execute, args=(run,), daemon=True).start()
        return run

    def execute(self, run):
        try:
            status, result = self.bridge.execute(run["flow"], run["id"])
        except subprocess.TimeoutExpired:
            status, result = "uncertain", {"message": "Quá thời gian; đối chiếu trạng thái trước khi thử lại."}
        except Exception as exc:
            status, result = "failed", {"error_type": type(exc).__name__, "message": "Luồng thất bại; kiểm tra log cục bộ."}
        self.store.finish(run["id"], status, result)
