"""Category-neutral copy: no fabricated price/performance or M31 images for other SKUs."""
from affiliate_domain.catalog import CATEGORIES


def shorten(value, limit):
    if len(value) <= limit:
        return value
    return value[:limit].rsplit(" ", 1)[0].strip()


def scenes(product):
    if any(not isinstance(product.get(k), str) or not product[k].strip() for k in ("title", "variant", "placement")):
        raise ValueError("Thiếu tên sản phẩm, biến thể hoặc vị trí link cho bộ dựng tổng quát.")
    title = shorten(product["title"], 44)
    variant = shorten(product["variant"], 40)
    summary = shorten(product.get("summary") or product["title"], 160)
    category = CATEGORIES.get(product.get("category"), "Sản phẩm")
    cta = "Mở link sản phẩm trên hồ sơ." if product["placement"] == "profile" else "Mở link sản phẩm trong bài đăng."
    rows = [("hook", title, category.upper(), "Bạn đang tìm " + title + "?"),
            ("product", title, "XEM ĐÚNG SẢN PHẨM", summary),
            ("options", variant, "BIẾN THỂ ĐÃ CHỌN", "Đây là lựa chọn " + variant + "."),
            ("case", "XEM CHI TIẾT", "THÔNG TIN TỪ TRANG SẢN PHẨM", "Xem chi tiết sản phẩm và lựa chọn phù hợp với bạn."),
            ("ending", title, "XEM SẢN PHẨM", cta)]
    return [dict(zip(("kind", "headline", "label", "voice"), row)) for row in rows]
