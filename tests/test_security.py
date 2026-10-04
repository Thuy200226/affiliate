from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from affiliate_control.security import COOKIE, Sessions


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.sessions = Sessions(Path(self.temp.name))
        self.token = self.sessions.issue()
        self.headers = {"Host": "127.0.0.1:8787", "Origin": "http://127.0.0.1:8787",
                        "Cookie": f"{COOKIE}={self.token}", "X-CSRF-Token": self.sessions.csrf(self.token)}
        self.hosts = {"127.0.0.1:8787"}

    def test_valid_local_request(self):
        self.assertTrue(self.sessions.authorize(self.headers, self.hosts, write=True))

    def test_cross_origin_cannot_execute(self):
        self.headers["Origin"] = "https://other.example"
        self.assertFalse(self.sessions.authorize(self.headers, self.hosts, write=True))

    def test_dns_rebinding_host_rejected(self):
        self.headers["Host"] = "attacker.example:8787"
        self.assertFalse(self.sessions.authorize(self.headers, self.hosts))

    def test_missing_csrf_and_tampered_cookie_rejected(self):
        self.headers.pop("X-CSRF-Token")
        self.assertFalse(self.sessions.authorize(self.headers, self.hosts, write=True))
        self.assertFalse(self.sessions.valid(self.token[:-1] + ("0" if self.token[-1] != "0" else "1")))

    def test_expired_session_and_key_survive_restart(self):
        with patch("affiliate_control.security.time.time", return_value=int(self.token.split(".")[0]) + 28801):
            self.assertFalse(self.sessions.valid(self.token))
        self.assertTrue(Sessions(Path(self.temp.name)).valid(self.token))
