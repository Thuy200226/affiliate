from http.client import HTTPConnection
import json
from pathlib import Path
import socket
import tempfile
import threading
import unittest
from unittest.mock import patch

from affiliate_control.application import Application
from affiliate_control.config import Settings
from affiliate_control.http import make_server


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            self.port = sock.getsockname()[1]
        self.app = Application(Settings(state=Path(self.temp.name), port=self.port))
        self.server = make_server(self.app)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        _, headers, _ = self.request("GET", "/")
        self.cookie = headers["Set-Cookie"].split(";")[0]
        token = self.cookie.split("=", 1)[1]
        self.headers = {"Cookie": self.cookie, "Origin": f"http://127.0.0.1:{self.port}",
                        "X-CSRF-Token": self.app.sessions.csrf(token), "Content-Type": "application/json"}

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, method, path, body=None, headers=None):
        connection = HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            connection.request(method, path, body=body, headers=headers or {})
            reply = connection.getresponse()
            return reply.status, dict(reply.getheaders()), reply.read()
        finally:
            connection.close()

    def test_api_requires_session_and_rejects_wrong_host(self):
        self.assertEqual(self.request("GET", "/api/runs")[0], 401)
        self.assertEqual(self.request("GET", "/health", headers={"Host": "other.example"})[0], 403)

    def test_cross_origin_action_cannot_reach_runner(self):
        headers = self.headers | {"Origin": "https://other.example"}
        with patch.object(self.app, "start") as start:
            status = self.request("POST", "/api/actions/readiness", "{}", headers)[0]
        self.assertEqual(status, 403)
        start.assert_not_called()

    def test_action_reservation_idempotent_and_body_bounded(self):
        body = json.dumps({"idempotency_key": "request_abcdefghijkl"})
        with patch.object(self.app.bridge, "eligible", return_value=(True, "")), patch.object(
                self.app, "execute", return_value=None):
            first = self.request("POST", "/api/actions/readiness", body, self.headers)
            second = self.request("POST", "/api/actions/readiness", body, self.headers)
        self.assertEqual(first[0], 202)
        self.assertEqual(json.loads(first[2])["run"]["id"], json.loads(second[2])["run"]["id"])
        self.assertEqual(self.request("POST", "/api/actions/readiness", "x" * 4097, self.headers)[0], 413)

    def test_static_paths_do_not_escape_root_and_headers_protect_console(self):
        status, headers, _ = self.request("GET", "/", headers={"Cookie": self.cookie})
        self.assertEqual(status, 200)
        self.assertIn("HttpOnly", headers["Set-Cookie"])
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertEqual(self.request("GET", "/../../private", headers=self.headers)[0], 404)
