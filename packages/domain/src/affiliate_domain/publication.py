from dataclasses import dataclass
from datetime import datetime, timezone
import re
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Product:
    shop_id: str
    item_id: str
    variant_id: str
    title: str


@dataclass(frozen=True)
class LinkEvidence:
    url: str
    affiliate_account_id: str
    shop_id: str
    item_id: str
    variant_id: str
    target_account_id: str
    platform: str
    placement: str
    proof_ref: str
    expires_at: datetime


def validate_link(product, evidence, owner, target, now=None):
    now = now or datetime.now(timezone.utc)
    parsed = urlsplit(evidence.url)
    if parsed.scheme != "https" or parsed.hostname not in ("s.shopee.vn", "shopee.vn"):
        raise ValueError("Not a supported owned affiliate destination")
    if parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError("Malformed destination")
    if evidence.affiliate_account_id != owner or evidence.target_account_id != target:
        raise ValueError("Link/account binding mismatch")
    if (evidence.shop_id, evidence.item_id, evidence.variant_id) != (product.shop_id, product.item_id, product.variant_id):
        raise ValueError("Wrong product or variant")
    if not evidence.proof_ref or evidence.expires_at.tzinfo is None or evidence.expires_at <= now:
        raise ValueError("Current owner-generated link evidence required")
    return True


def build_post(product, evidence, owner, target, hashtags, now=None):
    validate_link(product, evidence, owner, target, now)
    routes = {
        ("youtube_shorts", "profile"): "Chạm tên kênh → mở link sản phẩm trên hồ sơ.",
        ("youtube_long", "description"): "Xem sản phẩm: " + evidence.url,
        ("facebook_post", "body"): "Xem sản phẩm: " + evidence.url,
        ("instagram_reels", "profile"): "Mở hồ sơ → chạm link sản phẩm.",
        ("tiktok", "profile"): "Mở hồ sơ → chạm link sản phẩm.",
    }
    key = (evidence.platform, evidence.placement)
    if key not in routes:
        raise ValueError("Unverified/unsupported link placement")
    if not isinstance(hashtags, list) or not 1 <= len(hashtags) <= 5:
        raise ValueError("Choose one to five relevant tags from the reviewed brief")
    if any(not isinstance(tag, str) or not re.fullmatch(r"#[\w]{1,40}", tag) for tag in hashtags):
        raise ValueError("Invalid hashtag")
    return {"product": product.title, "cta": routes[key],
            "hashtags": list(dict.fromkeys(hashtags)), "link": evidence.url,
            "account_id": target, "platform": evidence.platform,
            "link_proof_ref": evidence.proof_ref}
