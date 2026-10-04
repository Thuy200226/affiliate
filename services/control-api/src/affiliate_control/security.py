"""One-owner loopback session, CSRF and browser response headers."""
import hashlib
import hmac
from http.cookies import SimpleCookie
import secrets
import time


COOKIE = "affiliate_console"


class Sessions:
    def __init__(self, state):
        path = state / "session.key"
        if not path.exists():
            with path.open("xb") as handle:
                handle.write(secrets.token_bytes(32))
            path.chmod(0o600)
        self.key = path.read_bytes()
        if len(self.key) != 32:
            raise ValueError("Invalid console session key")

    def sign(self, payload):
        return hmac.new(self.key, payload.encode(), hashlib.sha256).hexdigest()

    def issue(self):
        payload = f"{int(time.time())}.{secrets.token_hex(16)}"
        return f"{payload}.{self.sign(payload)}"

    def valid(self, token):
        try:
            timestamp, nonce, signature = token.split(".")
            age = time.time() - int(timestamp)
            return (0 <= age <= 28800 and len(nonce) == 32
                    and hmac.compare_digest(signature, self.sign(f"{timestamp}.{nonce}")))
        except (ValueError, AttributeError):
            return False

    def cookie_token(self, header):
        try:
            cookie = SimpleCookie(header or "")
            return cookie[COOKIE].value if COOKIE in cookie else ""
        except Exception:
            return ""

    def csrf(self, token):
        return self.sign("csrf:" + token)

    def authorize(self, headers, hosts, write=False):
        if headers.get("Host") not in hosts:
            return False
        token = self.cookie_token(headers.get("Cookie"))
        if not self.valid(token):
            return False
        if not write:
            return True
        origins = {"http://" + host for host in hosts}
        provided = headers.get("X-CSRF-Token", "")
        return (headers.get("Origin") in origins
                and hmac.compare_digest(provided, self.csrf(token)))


HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "same-origin",
    "Content-Security-Policy": "default-src 'self'; img-src 'self' https://i.ytimg.com https://down-vn.img.susercontent.com https://cf.shopee.vn; style-src 'self'; "
    "script-src 'self'; connect-src 'self'; frame-src https://www.youtube-nocookie.com https://www.tiktok.com; object-src 'none'; frame-ancestors 'none'; "
    "base-uri 'none'; form-action 'self'",
}
