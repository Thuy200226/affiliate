from .created_renderer import scene_plan


def initial(runtime):
    products = []
    if runtime:
        products.append({"id": "m31", "title": "Micro cài áo M31", "shop_id": "928446709",
                         "item_id": "24035184620", "variant": "Cần đối chiếu trước khi đăng",
                         "summary": "Micro cài áo cho điện thoại; chọn bộ và đầu cắm phù hợp.",
                         "category": "technology", "query": "micro M31 review", "image_url": "", "priority": "normal", "status": "active",
                         "affiliate_url": "https://s.shopee.vn/1AgidEiQP", "link_status": "needs_refresh",
                         "account": "@chungthuyao7335", "platform": "youtube_shorts", "placement": "profile"})
    return {"schema_version": 3, "affiliate_reports": [], "publication_controls": {}, "settings": {"query": "micro M31 review", "order": "relevance",
            "limit": 10, "confirmation_mode": "reuse_valid", "release_mode": "auto",
            "daily_enabled": False}, "products": products, "sources": [], "batches": []}


def initialize_branch(batch):
    if (batch["product"].get("shop_id"), batch["product"].get("item_id")) == ("928446709", "24035184620"):
        batch["branches"]["created"]["scenes"] = scene_plan(batch["product"])
    else:
        from .generic_plan import scenes
        batch["branches"]["created"]["scenes"] = scenes(batch["product"])
