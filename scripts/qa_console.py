"""Isolated UI review data. No live workflow, publisher, key write or account request."""
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
for folder in ("services/control-api/src", "packages/domain/src"):
    sys.path.insert(0, str(ROOT / folder))
from affiliate_control.application import Application
from affiliate_control.config import Settings
from affiliate_control.http import make_server
from affiliate_control.catalog_commands import save
from affiliate_control.content_commands import add_source, mutate


class OfflineBridge:
    def worker(self, _):
        return {}

    def snapshot(self, _):
        return {}

    def eligible(self, _):
        return False, "Môi trường kiểm thử cách ly · không gọi tài khoản thật."


def seed(state):
    state["products"], state["batches"], state["sources"] = [], [], []
    for category, title, item in (("fashion", "Áo khoác", "101"), ("home", "Hộp đựng", "102"), ("technology", "Micro", "103")):
        ident = save(state, {"title": "KIỂM THỬ · " + title, "summary": "Dữ liệu QA, không phải sản phẩm hoặc link bán thật.",
                           "shop_id": "999", "item_id": item, "variant": "Biến thể kiểm thử", "category": category,
                           "affiliate_url": "https://s.shopee.vn/TEST-NOT-AFFILIATE", "account": "@qa-not-a-real-account",
                           "platform": "youtube_shorts", "query": title + " QA"})["product_id"]
        batch = mutate(state, {"action": "batch", "data": {"product_id": ident}}, {})["batch_id"]
        source = add_source(state, {"product_id": ident, "url": "https://example.org/qa/" + item,
                                   "title": "MP4 do dự án tự tạo · kiểm thử nhận tệp", "creator": "QA fixture"})
        mutate(state, {"action": "select", "batch_id": batch, "kind": "selected", "data": {"source_id": source["id"]}}, {})
    return {}


def main():
    os.umask(0o077)
    with tempfile.TemporaryDirectory(prefix="affiliate-ui-qa-") as folder:
        settings = Settings(state=Path(folder), port=8788, runtime=Path("/Users/daothuy/affiliate-automation"))
        app = Application(settings, bridge=OfflineBridge())
        app.content.store.system_update(seed)
        for operation in ("save", "remove", "launch", "secret"):
            def blocked(*_):
                raise ValueError("Không thao tác tài khoản thật trong môi trường QA.")
            setattr(app.connections, operation, blocked)
        server = make_server(app)
        print("QA isolated: http://127.0.0.1:8788 — fixture only; live actions disabled", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == "__main__":
    main()
