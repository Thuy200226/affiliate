from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

from .application import UnavailableError
from .security import COOKIE, HEADERS
from .store import BusyError


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def reply(self, code, data, mime="application/json; charset=utf-8", cookie=None):
        payload = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        for key, value in HEADERS.items():
            self.send_header(key, value)
        if cookie:
            self.send_header("Set-Cookie", f"{COOKIE}={cookie}; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800")
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        app = self.server.app
        if self.headers.get("Host") not in app.settings.hosts:
            return self.reply(403, {"error": "Host không được phép."})
        if self.path == "/health":
            return self.reply(200, {"ok": True, "service": "affiliate-control"})
        static = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
                  "/style.css": ("style.css", "text/css")}
        if self.path in static:
            name, mime = static[self.path]
            token = app.sessions.cookie_token(self.headers.get("Cookie"))
            if not app.sessions.valid(token):
                token = app.sessions.issue()
            return self.reply(200, (app.settings.web / name).read_bytes(), mime + "; charset=utf-8", token)
        if not app.sessions.authorize(self.headers, app.settings.hosts):
            return self.reply(401, {"error": "Mở trang quản lý để tạo phiên."})
        if self.path == "/api/overview":
            token = app.sessions.cookie_token(self.headers.get("Cookie"))
            return self.reply(200, app.overview() | {"csrf_token": app.sessions.csrf(token)})
        if self.path == "/api/runs":
            return self.reply(200, {"runs": app.store.recent()})
        return self.reply(404, {"error": "Không có route này."})

    def do_POST(self):
        app = self.server.app
        if not app.sessions.authorize(self.headers, app.settings.hosts, write=True):
            return self.reply(403, {"error": "Phiên hoặc nguồn yêu cầu không hợp lệ."})
        if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            return self.reply(415, {"error": "Cần JSON."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 1 <= length <= 4096 or self.headers.get("Transfer-Encoding"):
                return self.reply(413, {"error": "Body vượt giới hạn."})
            body = json.loads(self.rfile.read(length))
            prefix = "/api/actions/"
            if not self.path.startswith(prefix):
                return self.reply(404, {"error": "Không có hành động này."})
            run = app.start(self.path[len(prefix):], body)
            return self.reply(202, {"run": run})
        except BusyError as exc:
            return self.reply(409, {"error": str(exc)})
        except UnavailableError as exc:
            return self.reply(412, {"error": str(exc)})
        except (ValueError, KeyError, TypeError):
            return self.reply(400, {"error": "Hành động hoặc dữ liệu không hợp lệ."})


def make_server(app):
    server = ThreadingHTTPServer((app.settings.bind, app.settings.port), Handler)
    server.app = app
    return server
