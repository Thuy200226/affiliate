import json
from pathlib import Path
from unittest.mock import Mock, patch
import unittest
import uuid

from affiliate_control.content_initial import initial
import test_http as http_fixtures


class ContentHTTPTests(unittest.TestCase):
    setUp = http_fixtures.HTTPTests.setUp
    tearDown = http_fixtures.HTTPTests.tearDown
    request = http_fixtures.HTTPTests.request

    def seed(self):
        body = {"expected_version": 1, "idempotency_key": str(uuid.uuid4())}
        self.app.content.store.command(body, lambda state: state.update(initial(Path(self.temp.name))) or {})

    def post(self, body):
        return self.request("POST", "/api/content/commands", json.dumps(body), self.headers)

    def test_workspace_session_csrf_and_unknown_data(self):
        self.assertEqual(self.request("GET", "/api/content")[0], 401)
        body = {"action": "batch", "data": {}, "expected_version": 1, "idempotency_key": str(uuid.uuid4())}
        self.assertEqual(self.request("POST", "/api/content/commands", json.dumps(body), {})[0], 403)
        self.assertEqual(self.post(body | {"data": {"path": "/tmp"}})[0], 400)
        self.assertEqual(self.post(body | {"action": ["not-string"]})[0], 400)
        self.assertEqual(self.post(body | {"data": None})[0], 400)

    def test_static_modules_and_xss_are_not_executable(self):
        for name in ("workspace.js", "source-view.js", "output-view.js", "settings-view.js", "media-preview.js", "results-view.js"):
            status, headers, _ = self.request("GET", "/" + name)
            self.assertEqual(status, 200)
            self.assertIn("script-src 'self'", headers["Content-Security-Policy"])
        self.assertEqual(self.request("GET", "/api/content/media/../../session.key", headers=self.headers)[0], 404)

    def test_media_range_history_and_containment(self):
        self.seed()
        body = {"action": "batch", "data": {"product_id": "m31"}, "expected_version": 2,
                "idempotency_key": str(uuid.uuid4())}
        batch = json.loads(self.post(body)[2])["batch_id"]
        folder = Path(self.temp.name) / "media"
        folder.mkdir()
        (folder / "fixture.mp4").write_bytes(b"0123456789")
        def add(state):
            state["batches"][0]["branches"]["created"]["artifact"] = {"relative_path": "media/fixture.mp4"}
            return {}
        self.app.content.store.command({"expected_version": 3, "idempotency_key": str(uuid.uuid4())}, add)
        url = f"/api/content/media/{batch}/created/1"
        self.assertEqual(self.request("GET", url)[0], 401)
        status, headers, payload = self.request("GET", url, headers=self.headers | {"Range": "bytes=2-4"})
        self.assertEqual((status, payload, headers["Content-Range"]), (206, b"234", "bytes 2-4/10"))
        self.assertEqual(self.request("GET", url, headers=self.headers | {"Range": "bytes=12-"})[0], 416)
        def escape(state):
            state["batches"][0]["branches"]["created"]["artifact"]["relative_path"] = "../private.mp4"
            return {}
        self.app.content.store.command({"expected_version": 4, "idempotency_key": str(uuid.uuid4())}, escape)
        self.assertEqual(self.request("GET", url, headers=self.headers)[0], 404)

    def test_render_enqueued_once_from_duplicate_request(self):
        self.seed()
        body = {"action": "batch", "data": {"product_id": "m31"}, "expected_version": 2,
                "idempotency_key": str(uuid.uuid4())}
        batch = json.loads(self.post(body)[2])["batch_id"]
        process = body | {"action": "process", "data": {}, "expected_version": 3,
                          "batch_id": batch, "kind": "created", "idempotency_key": str(uuid.uuid4())}
        with patch.object(self.app.content, "capabilities", return_value={"created_renderer": True}), patch(
                "affiliate_control.content.Thread") as worker:
            one, two = self.post(process), self.post(process)
        self.assertEqual((one[0], two[0]), (200, 200))
        self.assertEqual(json.loads(one[2]), json.loads(two[2]))
        worker.assert_called_once()

    def test_preview_disconnect_is_normal_not_server_failure(self):
        from affiliate_control.media_http import write_range
        file = Path(self.temp.name) / "preview.mp4"
        file.write_bytes(b"test-preview")
        for error in (BrokenPipeError, ConnectionResetError):
            handler = Mock()
            handler.wfile.write.side_effect = error()
            write_range(handler, file, 0, 11)
            handler.wfile.write.assert_called_once_with(b"test-preview")
