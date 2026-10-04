from unittest.mock import Mock
import unittest

from affiliate_control.overview import post_record, summarize


class OverviewTests(unittest.TestCase):
    def test_per_post_time_and_unknown_attribution(self):
        row = post_record({"video_id": "abcdefghijk", "total_platform_views": "0",
                           "confirmed_affiliate_commission": 999}, {"checked_at": "source-time"})
        self.assertEqual(row["total_platform_views"], "0")
        self.assertEqual(row["observed_at"], "source-time")
        for key in ("likes", "comments", "average_percentage_viewed", "affiliate_clicks", "confirmed_affiliate_commission"):
            self.assertIsNone(row[key])

    def test_oauth_failure_preserves_old_metrics_and_excludes_test_video(self):
        records = {"artifacts/current-published-videos.json": {"checked_at": "2020-01-01T00:00:00+00:00", "videos": [
            {"video_id": "abcdefghijk", "kind": "affiliate", "privacy_status": "public", "total_platform_views": "42"},
            {"video_id": "01234567890", "kind": "technical_test_not_affiliate", "total_platform_views": "99"}]},
            "artifacts/rerun-readiness.json": {"ok": False, "error_type": "NodeApiError"}}
        bridge = Mock()
        bridge.worker.return_value = {}
        bridge.snapshot.side_effect = lambda path: records.get(path, {})
        bridge.eligible.return_value = (False, "not-connected")
        data = summarize(bridge)
        self.assertFalse(data["snapshot_fresh"])
        self.assertEqual(len(data["videos"]), 1)
        self.assertEqual(data["videos"][0]["total_platform_views"], "42")
        self.assertIn("lỗi xác thực", data["metrics_error"])
        self.assertIsNone(data["confirmed_commission"])
