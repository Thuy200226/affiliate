"""Real workspace actions; unconnected publishing/Flow steps remain explicit blockers."""
from copy import deepcopy
import threading
from threading import Thread

from affiliate_domain.two_video import process_blockers, stamp
from .content_commands import find, mutate
from .content_initial import initial
from .content_store import ContentStore
from .content_edits import validate_body
from . import created_renderer, discovery


class Content:
    def __init__(self, settings):
        self.settings = settings
        self.store = ContentStore(settings.state / "content.sqlite", initial(settings.runtime))
        self.search_lock = threading.Lock()

    def capabilities(self):
        return {"created_renderer": created_renderer.available(self.settings.runtime),
                "video_search": discovery.configured(), "flow_runner": False,
                "publish_public": False, "daily": False}

    def read(self):
        state = self.store.read()
        caps = self.capabilities()
        for batch in state["batches"]:
            for branch in batch["branches"].values():
                branch["process_blockers"] = process_blockers(branch, caps)
                branch["release_blockers"] = ["Link/SKU cần đối chiếu mới.", "Publisher hai nhánh chưa nối; không tự công khai."]
                if not branch.get("artifact"):
                    branch["release_blockers"].insert(0, "Chưa có tệp hoàn chỉnh.")
                elif not branch["artifact"].get("perceptual_reviewed"):
                    branch["release_blockers"].insert(0, "Cần xem/nghe bản này.")
                if branch["hold"]:
                    branch["release_blockers"].insert(0, "Bạn đang giữ bản này.")
        return state | {"capabilities": caps}

    def post(self, body):
        allowed = {"action", "data", "batch_id", "kind", "expected_version", "idempotency_key"}
        if not isinstance(body, dict) or set(body) - allowed or not isinstance(body.get("data", {}), dict):
            raise ValueError("Dữ liệu workspace không hợp lệ.")
        validate_body(body)
        if body.get("action") == "search":
            return self.search(body)
        result, created = self.store.command(body, lambda state: mutate(state, body, self.capabilities()))
        if created and body["action"] == "process":
            state = self.store.read()
            batch = find(state["batches"], result["batch_id"])
            branch = batch["branches"][result["kind"]]
            if branch["revision"] != result["revision"] or branch["run_id"] != result["run_id"]:
                return result
            Thread(target=self.render, args=(deepcopy(batch), deepcopy(branch)), daemon=True).start()
        return result

    def search(self, body):
        from .content_commands import add_source
        with self.search_lock:
            prior = self.store.prior_command(body)
            if prior is not None:
                return prior
            state = self.store.read()
            find(state["products"], body.get("data", {}).get("product_id"))
            if state["version"] != body.get("expected_version"):
                from .store import BusyError
                raise BusyError("Profile đã đổi; làm mới trước khi tìm.")
            items = discovery.search(state["settings"])
            def apply(current):
                sources = [add_source(current, item | {"product_id": body["data"]["product_id"]}) for item in items]
                current["last_search"] = {"query": state["settings"]["query"], "at": stamp(), "count": len(sources)}
                return {"source_ids": [s["id"] for s in sources], "count": len(sources)}
            result, _ = self.store.command(body, apply)
            return result

    def render(self, batch, branch):
        def update(data):
            return self.store.worker_update(batch["id"], branch["kind"], branch["revision"], branch["run_id"], data)
        try:
            artifact = created_renderer.render(self.settings.runtime, self.settings.state, batch, branch,
                                                lambda step: update({"notes": [step]}))
            update({"status": "ready", "artifact": artifact, "completed_at": stamp(),
                    "notes": ["Dựng và kiểm kỹ thuật xong; xem/nghe trước khi đăng."]})
        except Exception as exc:
            update({"status": "failed", "notes": ["Dựng chưa đạt; xem nhật ký cục bộ, làm lại bằng revision mới."],
                    "error_type": type(exc).__name__, "completed_at": stamp()})
