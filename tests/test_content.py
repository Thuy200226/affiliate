from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import uuid

from affiliate_control.config import Settings
from affiliate_control.content import Content
from affiliate_control.content_initial import initial
from affiliate_control.content_store import ContentStore
from affiliate_control.store import BusyError


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        with patch("affiliate_control.content.initial", return_value=initial(Path(self.temp.name))):
            self.app = Content(Settings(state=Path(self.temp.name)))

    def command(self, action, data=None, kind=None, batch_id=None):
        body = {"action": action, "data": data or {}, "expected_version": self.app.store.read()["version"],
                "idempotency_key": str(uuid.uuid4())}
        if kind:
            body.update(kind=kind, batch_id=batch_id)
        return body, self.app.post(body)

    def batch(self):
        return self.command("batch", {"product_id": "m31"})[1]["batch_id"]

    def source(self):
        return self.command("source", {"product_id": "m31", "title": "Observed review",
                                      "url": "https://www.youtube.com/shorts/ddY5Hh29VhE"})[1]["source_id"]

    def test_idempotent_replay_and_version_conflict(self):
        body, first = self.command("batch", {"product_id": "m31"})
        self.assertEqual(self.app.post(body), first)
        self.assertEqual(len(self.app.store.read()["batches"]), 1)
        with self.assertRaises(ValueError):
            self.app.post(body | {"action": "hold"})
        with self.assertRaises(BusyError):
            self.app.post(body | {"idempotency_key": str(uuid.uuid4())})

    def test_manual_source_cannot_spoof_provider_provenance(self):
        with self.assertRaises(ValueError):
            self.command("source", {"method": "youtube_data_api"})
        source_id = self.source()
        row = self.app.store.read()["sources"][0]
        self.assertEqual(row["method"], "owner_entry_not_provider_verified")
        self.assertIsNone(row["views"])
        self.assertEqual(row["id"], source_id)

    def test_selected_changes_preserve_created_and_reuse_confirmation(self):
        batch_id, source_id = self.batch(), self.source()
        self.command("select", {"source_id": source_id}, "selected", batch_id)
        self.command("confirm", {"media_audio": True}, "selected", batch_id)
        second = self.batch()
        created = deepcopy(self.app.store.read()["batches"][-1]["branches"]["created"])
        self.command("select", {"source_id": source_id}, "selected", second)
        branches = self.app.store.read()["batches"][-1]["branches"]
        self.assertEqual(branches["created"], created)
        self.assertIsNotNone(branches["selected"]["confirmation"])
        with self.assertRaises(ValueError):
            self.command("process", {}, "selected", second)

    def test_worker_fencing_hold_restart(self):
        batch_id = self.batch()
        with patch.object(self.app, "capabilities", return_value={"created_renderer": True}), patch(
                "affiliate_control.content.Thread"):
            _, result = self.command("process", {}, "created", batch_id)
        self.command("hold", {}, "created", batch_id)
        args = (batch_id, "created", result["revision"], result["run_id"])
        self.assertTrue(self.app.store.worker_update(*args, {"status": "ready", "artifact": {"sha256": "test"}}))
        self.assertTrue(self.app.store.read()["batches"][0]["branches"]["created"]["hold"])
        self.command("revise", {}, "created", batch_id)
        self.assertFalse(self.app.store.worker_update(*args, {"status": "ready"}))
        reopened = ContentStore(self.app.store.path, {})
        self.assertEqual(reopened.read(), self.app.store.read())

    def test_search_replay_does_not_call_provider_twice(self):
        item = {"title": "M31", "creator": "Public creator", "method": "youtube_data_api",
                "url": "https://www.youtube.com/watch?v=ddY5Hh29VhE"}
        with patch("affiliate_control.discovery.search", return_value=[item]) as search:
            body, first = self.command("search", {"product_id": "m31"})
            self.assertEqual(self.app.post(body), first)
        search.assert_called_once()

    def test_unknown_fields_no_state_mutation(self):
        before = self.app.store.read()
        for action, data in (("batch", {"product_id": "m31", "path": "/tmp"}), ("launch", {})):
            with self.assertRaises(ValueError):
                self.command(action, data)
        self.assertEqual(before, self.app.store.read())

    def test_recovery_marks_interrupted_without_starting_worker(self):
        batch_id = self.batch()
        with patch.object(self.app, "capabilities", return_value={"created_renderer": True}), patch(
                "affiliate_control.content.Thread") as worker:
            self.command("process", {}, "created", batch_id)
        worker.assert_called_once()
        self.app.store.recover()
        state = self.app.store.read()
        self.assertEqual(state["batches"][0]["branches"]["created"]["status"], "interrupted")
        with self.assertRaises(ValueError):
            self.command("process", {}, "created", batch_id)

    def test_copy_edit_requires_new_review_but_preserves_media(self):
        batch_id = self.batch()
        with patch.object(self.app, "capabilities", return_value={"created_renderer": True}), patch(
                "affiliate_control.content.Thread"):
            _, run = self.command("process", {}, "created", batch_id)
        artifact = {"sha256": "checked", "perceptual_reviewed": True}
        self.app.store.worker_update(batch_id, "created", run["revision"], run["run_id"],
                                     {"status": "ready", "artifact": artifact})
        self.command("copy", {"title": "M31", "description": "Bộ micro", "hashtags": "#M31 #M31"}, "created", batch_id)
        branch = self.app.store.read()["batches"][0]["branches"]["created"]
        self.assertEqual(branch["artifact"]["sha256"], "checked")
        self.assertFalse(branch["artifact"]["perceptual_reviewed"])
        self.assertEqual(branch["copy"]["hashtags"], ["#M31"])
        with self.assertRaises(ValueError):
            self.command("review", {"sha256": "other", "watched_listened": True}, "created", batch_id)
