"""Additive migration; no historic branch payload/hash is rewritten."""
def upgrade(state):
    if state.get("schema_version", 1) >= 3:
        return False
    for product in state["products"]:
        product.setdefault("category", "technology" if product["id"] == "m31" else "other")
        product.setdefault("query", product["title"] + " review")
        product.setdefault("image_url", "")
        product.setdefault("priority", "normal")
        product.setdefault("status", "active")
    state.setdefault("affiliate_reports", [])
    state.setdefault("publication_controls", {})
    state["schema_version"] = 3
    return True
