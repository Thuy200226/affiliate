"""Persist run reservations and results, without credentials or execution output."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import re
import sqlite3
import uuid


class BusyError(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path):
        self.path = path
        with self.connection() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY, request_key TEXT UNIQUE NOT NULL,
                flow TEXT NOT NULL, status TEXT NOT NULL, started_at TEXT NOT NULL,
                completed_at TEXT, result TEXT NOT NULL DEFAULT '{}')""")

    @contextmanager
    def connection(self):
        with sqlite3.connect(self.path, timeout=5) as db:
            db.row_factory = sqlite3.Row
            yield db

    def reserve(self, flow, key):
        self.validate_key(key)
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            previous = db.execute("SELECT * FROM runs WHERE request_key=?", (key,)).fetchone()
            if previous:
                if previous["flow"] != flow:
                    raise ValueError("Key belongs to another action")
                return self.serialize(previous), False
            if db.execute("SELECT 1 FROM runs WHERE status='running'").fetchone():
                raise BusyError("Một luồng đang chạy; chờ kết quả trước khi chạy tiếp.")
            ident = str(uuid.uuid4())
            db.execute("INSERT INTO runs (id,request_key,flow,status,started_at) VALUES (?,?,?,?,?)",
                       (ident, key, flow, "running", now()))
            row = db.execute("SELECT * FROM runs WHERE id=?", (ident,)).fetchone()
            return self.serialize(row), True

    def find(self, flow, key):
        self.validate_key(key)
        with self.connection() as db:
            row = db.execute("SELECT * FROM runs WHERE request_key=?", (key,)).fetchone()
            if row and row["flow"] != flow:
                raise ValueError("Key belongs to another action")
            return self.serialize(row) if row else None

    @staticmethod
    def validate_key(key):
        if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9_-]{16,100}", key):
            raise ValueError("Invalid idempotency key")

    def finish(self, ident, status, result):
        if status not in ("succeeded", "failed", "uncertain"):
            raise ValueError("Invalid terminal state")
        with self.connection() as db:
            db.execute("UPDATE runs SET status=?,completed_at=?,result=? WHERE id=? AND status='running'",
                       (status, now(), json.dumps(result, ensure_ascii=False), ident))

    def recover(self):
        with self.connection() as db:
            db.execute("UPDATE runs SET status='interrupted',completed_at=? WHERE status='running'", (now(),))

    def recent(self):
        with self.connection() as db:
            return [self.serialize(row) for row in db.execute(
                "SELECT * FROM runs ORDER BY started_at DESC LIMIT 50")]

    @staticmethod
    def serialize(row):
        return {key: row[key] for key in ("id", "flow", "status", "started_at", "completed_at")} | {
            "result": json.loads(row["result"])}
