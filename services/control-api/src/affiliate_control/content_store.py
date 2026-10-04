"""Private, transactional workspace; version check prevents lost updates across tabs."""
from contextlib import contextmanager
import hashlib
import json
import sqlite3

from .store import BusyError


class ContentStore:
    def __init__(self, path, initial):
        self.path = path
        with self.connection() as db:
            db.execute("CREATE TABLE IF NOT EXISTS workspace (id INTEGER PRIMARY KEY, version INTEGER, data TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS commands (key TEXT PRIMARY KEY, digest TEXT, result TEXT)")
            db.execute("INSERT OR IGNORE INTO workspace VALUES (1,1,?)", (json.dumps(initial, ensure_ascii=False),))

    @contextmanager
    def connection(self):
        with sqlite3.connect(self.path, timeout=10) as db:
            db.row_factory = sqlite3.Row
            yield db

    def read(self):
        with self.connection() as db:
            row = db.execute("SELECT * FROM workspace WHERE id=1").fetchone()
            return json.loads(row["data"]) | {"version": row["version"]}

    def prior_command(self, body):
        from .store import Store
        Store.validate_key(body.get("idempotency_key"))
        digest = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        with self.connection() as db:
            prior = db.execute("SELECT * FROM commands WHERE key=?", (body["idempotency_key"],)).fetchone()
            if not prior:
                return None
            if prior["digest"] != digest:
                raise ValueError("Mã yêu cầu đã dùng cho nội dung khác.")
            return json.loads(prior["result"])

    def command(self, body, mutate):
        from .store import Store
        Store.validate_key(body.get("idempotency_key"))
        digest = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute("SELECT * FROM commands WHERE key=?", (body["idempotency_key"],)).fetchone()
            if prior:
                if prior["digest"] != digest:
                    raise ValueError("Mã yêu cầu đã dùng cho nội dung khác.")
                return json.loads(prior["result"]), False
            row = db.execute("SELECT * FROM workspace WHERE id=1").fetchone()
            if type(body.get("expected_version")) is not int or row["version"] != body["expected_version"]:
                raise BusyError("Dữ liệu đã đổi; làm mới rồi thử lại, không ghi đè lựa chọn.")
            state = json.loads(row["data"])
            result = mutate(state)
            db.execute("UPDATE workspace SET data=?,version=version+1 WHERE id=1", (json.dumps(state, ensure_ascii=False),))
            result = result | {"version": row["version"] + 1}
            db.execute("INSERT INTO commands VALUES (?,?,?)", (body["idempotency_key"], digest, json.dumps(result)))
            return result, True

    def worker_update(self, batch_id, kind, revision, run_id, update):
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM workspace WHERE id=1").fetchone()
            state = json.loads(row["data"])
            batch = next((b for b in state["batches"] if b["id"] == batch_id), None)
            branch = batch["branches"][kind] if batch else None
            if not branch or branch["revision"] != revision or branch["run_id"] != run_id:
                return False
            branch.update(update)
            db.execute("UPDATE workspace SET data=?,version=version+1 WHERE id=1", (json.dumps(state, ensure_ascii=False),))
            return True

    def recover(self):
        with self.connection() as db:
            row = db.execute("SELECT * FROM workspace WHERE id=1").fetchone()
            state = json.loads(row["data"])
            changed = False
            for batch in state["batches"]:
                for branch in batch["branches"].values():
                    if branch["status"] == "processing":
                        branch.update(status="interrupted", notes=["Bị ngắt; tạo revision mới trước khi thử lại."])
                        changed = True
            if changed:
                db.execute("UPDATE workspace SET data=?,version=version+1 WHERE id=1", (json.dumps(state, ensure_ascii=False),))
