"""Read-model checks use current catalog, while historic batch snapshots remain immutable."""
from affiliate_domain.catalog import binding_status
from affiliate_domain.source_links import provider
from affiliate_domain.two_video import process_blockers


def enrich(state, capabilities):
    for source in state["sources"]:
        source["provider"] = provider(source["url"])
    for product in state["products"]:
        product["link_check"] = binding_status(product)
    for batch in state["batches"]:
        current = next((p for p in state["products"] if p["id"] == batch["product"]["id"]), None)
        fields = ("affiliate_url", "shop_id", "item_id", "variant", "account", "platform", "placement")
        matches = current and all(current.get(k) == batch["product"].get(k) for k in fields)
        link_reason = (binding_status(current) if matches else "Catalog/link đã khác snapshot batch; tạo batch mới hoặc đối chiếu bản cũ riêng.")
        for branch in batch["branches"].values():
            branch["process_blockers"] = process_blockers(branch, capabilities)
            release = ["Publisher hai nhánh chưa nối; không tự công khai."]
            if not link_reason.startswith("Chủ đã"):
                release.insert(0,link_reason)
            if current and current.get("status") == "skipped":
                branch["process_blockers"].insert(0,"Sản phẩm đã bỏ qua; khôi phục và bỏ giữ trước xử lý.")
                release.insert(0,"Sản phẩm đang bỏ qua.")
            artifact = branch.get("artifact")
            if not artifact:
                release.insert(0,"Chưa có tệp hoàn chỉnh.")
            elif not artifact.get("perceptual_reviewed"):
                release.insert(0,"Cần xem/nghe bản này.")
            if branch["hold"]:
                release.insert(0,"Bạn đang giữ bản này.")
            branch["release_blockers"] = release
            branch["link_check"] = link_reason
    return state | {"capabilities":capabilities}
