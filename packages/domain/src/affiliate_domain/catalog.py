"""Product identity and owner-selected priority, never inferred from a video title."""
from datetime import datetime, timedelta, timezone
import re
from urllib.parse import urlsplit
import uuid

from .two_video import stamp, text

CATEGORIES = {"technology": "Công nghệ", "fashion": "Thời trang", "home": "Nhà cửa",
              "beauty": "Làm đẹp", "sports": "Thể thao", "other": "Khác"}
FIELDS = {"product_id", "title", "category", "summary", "shop_id", "item_id", "variant",
          "affiliate_url", "account", "platform", "placement", "query", "image_url"}


def affiliate_url(value):
    parsed = urlsplit(text(value, 500))
    if (parsed.scheme != "https" or parsed.hostname not in ("s.shopee.vn", "shopee.vn")
            or parsed.username or parsed.password or parsed.port not in (None, 443)):
        raise ValueError("Nhập link Shopee Affiliate HTTPS từ chính tài khoản của bạn.")
    return value.strip()


def validate_product(data):
    if set(data) - FIELDS:
        raise ValueError("Trường sản phẩm chưa hỗ trợ.")
    if data.get("category") not in CATEGORIES:
        raise ValueError("Chọn nhóm hàng.")
    for name in ("shop_id", "item_id"):
        if not isinstance(data.get(name), str) or not re.fullmatch(r"[0-9]{1,20}", data[name]):
            raise ValueError("Shop ID và Item ID phải đúng mã sản phẩm Shopee.")
    platform = data.get("platform", "youtube_shorts")
    routes = {"youtube_shorts": "profile", "youtube_long": "description", "tiktok": "profile",
              "instagram_reels": "profile", "facebook_post": "body"}
    if platform not in routes or data.get("placement", routes[platform]) != routes[platform]:
        raise ValueError("Vị trí link chưa phù hợp nền tảng.")
    result = {"id": data.get("product_id") or str(uuid.uuid4()), "title": text(data["title"], 95),
              "category": data["category"], "summary": text(data.get("summary", ""), 800, 0),
              "shop_id": data["shop_id"], "item_id": data["item_id"],
              "variant": text(data["variant"], 120), "affiliate_url": affiliate_url(data["affiliate_url"]),
              "account": text(data.get("account", "@chungthuyao7335"), 120),
              "platform": platform, "placement": routes[platform],
              "query": text(data.get("query") or data["title"] + " review", 250),
              "priority": "normal", "status": "active", "link_status": "needs_verification"}
    image = text(data.get("image_url", ""), 500, 0)
    if image:
        parsed = urlsplit(image)
        if (parsed.scheme != "https" or parsed.hostname not in ("down-vn.img.susercontent.com", "cf.shopee.vn")
                or parsed.username or parsed.password or parsed.port not in (None, 443)):
            raise ValueError("Ảnh URL hiện hỗ trợ CDN Shopee; không nhập URL nội bộ hoặc có đăng nhập.")
    return result | {"image_url": image, "updated_at": stamp()}


def verify_binding(product, data):
    expected = (product["affiliate_url"], product["shop_id"], product["item_id"], product["variant"], product["account"])
    actual = tuple(data.get(key) for key in ("affiliate_url", "shop_id", "item_id", "variant", "account"))
    if actual != expected or data.get("owner_generated") is not True or data.get("destination_checked") is not True:
        raise ValueError("Link, Shop/Item, biến thể hoặc tài khoản không khớp; cần đối chiếu thật.")
    return {"method": "owner_attestation_not_provider_verified", "url": product["affiliate_url"],
            "shop_id": product["shop_id"], "item_id": product["item_id"], "variant": product["variant"],
            "account": product["account"], "checked_at": stamp(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()}


def binding_status(product):
    evidence = product.get("link_evidence")
    if not evidence:
        return "Chưa đối chiếu link theo sản phẩm"
    for key in ("shop_id", "item_id", "variant", "account"):
        if evidence.get(key) != product.get(key):
            return "Không khớp sản phẩm/tài khoản"
    if evidence.get("url") != product.get("affiliate_url"):
        return "Link đã đổi, cần kiểm tra lại"
    try:
        if datetime.fromisoformat(evidence["expires_at"]) <= datetime.now(timezone.utc):
            return "Đối chiếu đã hết hạn"
    except (KeyError, ValueError, TypeError):
        return "Bằng chứng link không hợp lệ"
    return "Chủ đã đối chiếu · chưa xác minh bằng API"
