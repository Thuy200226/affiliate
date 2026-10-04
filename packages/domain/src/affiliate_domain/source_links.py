"""Reference URLs from multiple providers; accepting a URL is not permission to download."""
import ipaddress
import re
from urllib.parse import parse_qs, parse_qsl, urlencode, urlsplit


def normalize(value):
    from .two_video import text
    parsed = urlsplit(text(value, 1000))
    host = parsed.hostname or ""
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError("Cần URL HTTPS không chứa thông tin đăng nhập.")
    if host == "localhost" or host.endswith((".localhost", ".local", ".internal")) or "." not in host:
        raise ValueError("Không nhận địa chỉ nội bộ làm nguồn video.")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise ValueError("Không nhận địa chỉ IP nội bộ.")
    if host in ("www.youtube.com", "youtube.com", "youtu.be"):
        ident = (parsed.path.lstrip("/") if host == "youtu.be" else
                 parsed.path.split("/")[2] if parsed.path.startswith("/shorts/") else
                 parse_qs(parsed.query).get("v", [""])[0])
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", ident):
            raise ValueError("URL YouTube chưa có ID video hợp lệ.")
        return "https://www.youtube.com/watch?v=" + ident
    if host in ("www.tiktok.com", "tiktok.com"):
        if not re.fullmatch(r"/@[A-Za-z0-9_.-]+/video/[0-9]{10,25}/?", parsed.path):
            raise ValueError("Dùng URL TikTok đầy đủ có /@tên/video/ID.")
        return "https://www.tiktok.com" + parsed.path.rstrip("/")
    if host in ("www.instagram.com", "instagram.com"):
        if not re.fullmatch(r"/(?:reel|p)/[A-Za-z0-9_-]{5,60}/?", parsed.path):
            raise ValueError("Dùng URL bài hoặc Reel Instagram cụ thể.")
        return "https://www.instagram.com" + parsed.path.rstrip("/") + "/"
    if not parsed.path or parsed.path == "/":
        raise ValueError("Dùng URL trang/video cụ thể, không chỉ trang chủ.")
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    if any(k.lower() in ("access_token", "token", "key", "api_key", "password", "cookie", "code") for k,_ in pairs):
        raise ValueError("Không lưu URL chứa khoá hoặc thông tin đăng nhập.")
    pairs = [(k,v) for k,v in pairs if not k.lower().startswith("utm_") and k.lower() not in ("tracking","fbclid","gclid","si")]
    # References from any public website remain visible; no generic server download or iframe.
    return "https://" + host + parsed.path + ("?" + urlencode(pairs) if pairs else "")


def provider(value):
    host = urlsplit(value).hostname or ""
    if host in ("youtube.com", "www.youtube.com", "youtu.be"):
        return "YouTube"
    if host in ("tiktok.com", "www.tiktok.com"):
        return "TikTok"
    if host in ("instagram.com", "www.instagram.com"):
        return "Instagram"
    if host in ("facebook.com", "www.facebook.com", "fb.watch"):
        return "Facebook"
    if host in ("vimeo.com", "www.vimeo.com"):
        return "Vimeo"
    return host
