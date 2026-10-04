from copy import deepcopy
from datetime import datetime, timedelta, timezone
import unittest

from affiliate_domain.two_video import confirm_source, invalidate, new_batch, process_blockers, select_source, source_url


class TwoVideoTests(unittest.TestCase):
    def setUp(self):
        self.batch = new_batch({"id": "m31", "title": "Micro M31"}, {"query": "micro M31 review"})
        self.source = {"id": "source1", "product_id": "m31", "url": "https://www.youtube.com/watch?v=ddY5Hh29VhE"}

    def test_exactly_two_independent_branches_and_snapshot(self):
        self.assertEqual(set(self.batch["branches"]), {"created", "selected"})
        created = deepcopy(self.batch["branches"]["created"])
        select_source(self.batch, self.source)
        self.assertEqual(created, self.batch["branches"]["created"])
        self.assertEqual(self.batch["branches"]["selected"]["revision"], 2)
        select_source(self.batch, self.source)
        self.assertEqual(self.batch["branches"]["selected"]["revision"], 2)

    def test_wrong_product_source_rejected(self):
        with self.assertRaises(ValueError):
            select_source(self.batch, self.source | {"product_id": "other"})

    def test_confirmation_is_owner_scope_not_file_proof(self):
        select_source(self.batch, self.source)
        branch = self.batch["branches"]["selected"]
        with self.assertRaises(ValueError):
            confirm_source(branch, self.source, {})
        confirm_source(branch, self.source, {"media_audio": True})
        self.assertIsNone(branch["confirmation"]["asset_hash"])
        self.assertFalse(branch["confirmation"]["person_edit"])
        self.assertIn("runner Flow", process_blockers(branch, {"flow_runner": True})[0])
        branch["confirmation"]["expires_at"] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        self.assertIn("hết hạn", process_blockers(branch, {})[0])

    def test_hold_and_history_survive_revision(self):
        branch = self.batch["branches"]["created"]
        branch.update(hold=True, status="ready", artifact={"sha256": "old"})
        invalidate(branch)
        self.assertTrue(branch["hold"])
        self.assertIsNone(branch["artifact"])
        self.assertEqual(branch["history"][0]["artifact"]["sha256"], "old")
        self.assertIn("giữ", process_blockers(branch, {"created_renderer": True})[0])

    def test_normalize_only_supported_provider_video_urls(self):
        self.assertEqual(source_url("https://youtu.be/ddY5Hh29VhE?t=1"), self.source["url"])
        for url in ("http://youtube.com/watch?v=ddY5Hh29VhE", "https://evil.test/file.mp4",
                    "https://x@youtUbe.com/watch?v=ddY5Hh29VhE", "https://youtube.com:123/watch?v=ddY5Hh29VhE"):
            with self.assertRaises(ValueError):
                source_url(url)

    def test_completed_branch_does_not_render_twice(self):
        branch = self.batch["branches"]["created"]
        self.assertEqual(process_blockers(branch, {"created_renderer": True}), [])
        branch["status"] = "ready"
        self.assertTrue(process_blockers(branch, {"created_renderer": True}))

    def test_missing_confirmation_does_not_hide_unimplemented_flow(self):
        select_source(self.batch, self.source)
        reasons = process_blockers(self.batch["branches"]["selected"], {})
        self.assertTrue(any("chưa xác nhận" in reason for reason in reasons))
        self.assertTrue(any("runner Flow" in reason for reason in reasons))
