from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from affiliate_control.application import Application
from affiliate_control.config import Settings
from affiliate_control.store import BusyError, Store


class RunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "runs.sqlite"
        self.store = Store(self.path)

    def test_double_click_and_different_flow_cannot_reuse_key(self):
        first, created = self.store.reserve("readiness", "request_abcdefghijkl")
        again, created_again = self.store.reserve("readiness", "request_abcdefghijkl")
        self.assertTrue(created)
        self.assertFalse(created_again)
        self.assertEqual(first["id"], again["id"])
        with self.assertRaises(ValueError):
            self.store.reserve("media", "request_abcdefghijkl")

    def test_only_one_running_action_then_restart_preserves_result(self):
        run, _ = self.store.reserve("readiness", "request_abcdefghijkl")
        with self.assertRaises(BusyError):
            self.store.reserve("trends", "request_zyxwvutsrqpo")
        self.store.finish(run["id"], "succeeded", {"ok": True})
        restarted = Store(self.path)
        self.assertEqual(restarted.recent()[0]["result"], {"ok": True})
        self.assertTrue(restarted.reserve("trends", "request_zyxwvutsrqpo")[1])

    def test_crash_does_not_silently_retry(self):
        self.store.reserve("media", "request_abcdefghijkl")
        self.store.recover()
        run, created = self.store.reserve("media", "request_abcdefghijkl")
        self.assertFalse(created)
        self.assertEqual(run["status"], "interrupted")

    def test_completed_media_replay_works_after_queue_empty(self):
        app = Application(Settings(state=Path(self.temp.name)))
        run, _ = app.store.reserve("media", "request_abcdefghijkl")
        app.store.finish(run["id"], "succeeded", {"ok": True})
        with patch.object(app.bridge, "eligible", return_value=(False, "empty")) as guard:
            reply = app.start("media", {"idempotency_key": "request_abcdefghijkl"})
        guard.assert_not_called()
        self.assertEqual(reply["id"], run["id"])

    def test_arbitrary_command_and_extra_fields_rejected(self):
        app = Application(Settings(state=Path(self.temp.name)))
        with self.assertRaises(ValueError):
            app.start("shell", {"idempotency_key": "request_abcdefghijkl"})
        with self.assertRaises(ValueError):
            app.start("readiness", {"idempotency_key": "request_abcdefghijkl", "command": "anything"})
