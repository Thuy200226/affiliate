"""Local-only Keychain references and isolated Chrome profiles; never export cookies."""
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import subprocess
import threading

from affiliate_domain.two_video import stamp

TOOLS = {
    "youtube": ("YouTube", "https://studio.youtube.com/", "OAuth đăng/đọc dùng kết nối n8n hiện có"),
    "youtube_search": ("YouTube · tìm kiếm", "https://console.cloud.google.com/apis/credentials", "API key tìm kiếm YouTube"),
    "shopee": ("Shopee Affiliate", "https://affiliate.shopee.vn/", "Khoá đối tác nếu tài khoản được Shopee cấp API"),
    "flow": ("Google Flow", "https://labs.google/fx/tools/flow", "Phiên web Pro; API key không thay thế tín dụng Flow"),
    "gemini": ("Google AI Studio", "https://aistudio.google.com/", "Không tự bật thanh toán hoặc gọi API trả phí"),
    "tiktok": ("TikTok", "https://www.tiktok.com/", "Access token cần app và quyền đăng được duyệt"),
    "instagram": ("Instagram", "https://www.instagram.com/", "Token Meta cần đúng tài khoản và quyền"),
    "facebook": ("Facebook", "https://www.facebook.com/", "Token trang Meta; không tự đăng khi chưa kiểm chứng"),
    "n8n": ("n8n", "http://localhost:5678/home/credentials", "API key n8n; credential/OAuth quản lý trong n8n"),
}
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


class Connections:
    def __init__(self, settings):
        self.settings, self.lock = settings, threading.Lock()
        self.path = settings.state / "connections.sqlite"
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS metadata (tool TEXT PRIMARY KEY, saved_at TEXT)")

    def overview(self):
        with sqlite3.connect(self.path) as db:
            stored = dict(db.execute("SELECT tool,saved_at FROM metadata"))
        return {"tools": [{"id": ident, "title": name, "url": url, "help": help,
                 "key_saved": ident in stored, "saved_at": stored.get(ident), "api_verified": False,
                 "chrome_available": platform.system() == "Darwin" and CHROME.is_file(),
                 "session_status": "Có hồ sơ cục bộ; chưa xác minh đăng nhập" if
                 (self.settings.state / "browser-profiles" / ident).exists() else "Chưa mở hồ sơ riêng"}
                 for ident, (name, url, help) in TOOLS.items()]}

    def has(self, tool):
        with sqlite3.connect(self.path) as db:
            return db.execute("SELECT 1 FROM metadata WHERE tool=?", (tool,)).fetchone() is not None

    def binary(self):
        if platform.system() != "Darwin":
            raise ValueError("Lưu khoá bằng Keychain hiện chỉ có ở máy Mac; dùng secrets của dịch vụ trên máy khác.")
        source = Path(__file__).resolve().parents[2] / "native/vault.swift"
        folder = self.settings.state / "native"
        folder.mkdir(mode=0o700, exist_ok=True)
        file = folder / ("vault-" + hashlib.sha256(source.read_bytes()).hexdigest()[:16])
        if not file.exists():
            result = subprocess.run(["/usr/bin/swiftc", str(source), "-o", str(file)], capture_output=True, timeout=60)
            if result.returncode:
                raise ValueError("Chưa biên dịch được bộ lưu Keychain; không lưu khoá dưới dạng văn bản.")
            file.chmod(0o700)
        return file

    def secret(self, action, tool, value=None):
        if tool not in TOOLS or action not in ("save", "remove", "read"):
            raise ValueError("Công cụ chưa hỗ trợ.")
        with self.lock:
            result = subprocess.run([str(self.binary())], input=json.dumps({"action": action, "account": tool,
                                     "value": value}), text=True, capture_output=True, timeout=20)
        if result.returncode:
            raise ValueError("Keychain chưa cho phép thao tác; mở khoá hoặc cấp quyền trên máy. Giá trị không được ghi log.")
        return result.stdout if action == "read" else None

    def save(self, data):
        if set(data) != {"tool", "value"} or data["tool"] not in TOOLS:
            raise ValueError("Công cụ hoặc trường không hợp lệ.")
        value = data["value"]
        if not isinstance(value, str) or not 1 <= len(value.strip()) <= 8192 or any(ord(c) < 32 for c in value):
            raise ValueError("Khoá/token không hợp lệ.")
        self.secret("save", data["tool"], value.strip())
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT OR REPLACE INTO metadata VALUES (?,?)", (data["tool"], stamp()))
        return {"saved": True, "api_verified": False}

    def remove(self, data):
        if set(data) != {"tool"} or data["tool"] not in TOOLS:
            raise ValueError("Công cụ không hợp lệ.")
        self.secret("remove", data["tool"])
        with sqlite3.connect(self.path) as db:
            db.execute("DELETE FROM metadata WHERE tool=?", (data["tool"],))
        return {"removed": True}

    def launch(self, data):
        if set(data) != {"tool"} or data["tool"] not in TOOLS or not CHROME.is_file():
            raise ValueError("Công cụ hoặc Chrome chưa khả dụng.")
        profile = self.settings.state / "browser-profiles" / data["tool"]
        profile.mkdir(mode=0o700, parents=True, exist_ok=True)
        profile.chmod(0o700)
        subprocess.Popen([str(CHROME), "--user-data-dir=" + str(profile.resolve()), "--no-first-run",
                          "--no-default-browser-check", TOOLS[data["tool"]][1]],
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"opened": True, "logged_in_verified": False}
