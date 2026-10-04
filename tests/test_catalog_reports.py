from copy import deepcopy
from datetime import datetime, timedelta, timezone
import unittest

from affiliate_domain.catalog import binding_status
from affiliate_domain.source_links import normalize, provider
import test_content as fixtures


class CatalogTests(unittest.TestCase):
    setUp = fixtures.ContentTests.setUp
    command = fixtures.ContentTests.command
    batch = fixtures.ContentTests.batch
    source = fixtures.ContentTests.source

    def fields(self, **changes):
        return {"title": "Áo khoác", "category": "fashion", "shop_id": "123", "item_id": "456",
                "variant": "Màu xanh · M", "affiliate_url": "https://s.shopee.vn/example", "account": "@owner",
                "platform": "tiktok", "query": "áo khoác phối đồ", "summary": "Áo khoác màu xanh.", **changes}

    def test_multiple_categories_priority_skip_does_not_rewrite_snapshot(self):
        batch = self.batch()
        _, result = self.command("product", self.fields())
        product_id = result["product_id"]
        self.command("batch", {"product_id": product_id})
        before = deepcopy(self.app.store.read()["batches"][0])
        self.command("product_choice", {"product_id": product_id, "choice": "first"})
        self.command("product_choice", {"product_id": product_id, "choice": "skip"})
        self.assertEqual(self.app.store.read()["batches"][0], before)
        branches = self.app.store.read()["batches"][1]["branches"]
        self.assertTrue(all(b["hold"] for b in branches.values()))
        self.assertEqual(len(branches["created"]["scenes"]), 5)
        self.assertNotIn("M31", str(branches["created"]["scenes"]))
        with self.assertRaises(ValueError):
            self.command("batch", {"product_id": product_id})
        self.command("product_choice", {"product_id": product_id, "choice": "restore"})
        self.assertTrue(all(b["hold"] for b in self.app.store.read()["batches"][1]["branches"].values()))

    def test_dedupe_by_sku_variant_account_platform(self):
        self.command("product", self.fields())
        with self.assertRaises(ValueError):
            self.command("product", self.fields())
        self.command("product", self.fields(platform="instagram_reels"))
        self.command("product", self.fields(category="home", item_id="789"))
        self.assertEqual(len(self.app.store.read()["products"]), 4)

    def test_catalog_rejects_internal_images_extra_fields_wrong_link_route(self):
        for changes in ({"image_url":"http://localhost/file"}, {"affiliate_url":"https://evil.test/ref"},
                        {"placement":"description"}, {"category":"unknown"}, {"shop_id":1}, {"image_url":None}):
            with self.assertRaises(ValueError):
                self.command("product", self.fields(**changes))

    def test_link_binding_is_exact_expires_and_invalidates_after_edit(self):
        _, result = self.command("product", self.fields())
        ident = result["product_id"]
        data = {"product_id":ident, **{k:v for k,v in self.fields().items() if k in ("affiliate_url","shop_id","item_id","variant","account")},
                "owner_generated":True,"destination_checked":True}
        with self.assertRaises(ValueError):
            self.command("link_verify",data | {"item_id":"999"})
        self.command("link_verify",data)
        p = self.app.store.read()["products"][-1]
        self.assertIn("Chủ đã",binding_status(p))
        expired = deepcopy(p); expired["link_evidence"]["expires_at"] = (datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
        self.assertIn("hết hạn",binding_status(expired))
        self.command("product",self.fields(product_id=ident,affiliate_url="https://s.shopee.vn/changed"))
        self.assertIsNone(self.app.store.read()["products"][-1].get("link_evidence"))

    def test_per_product_query_reaches_provider(self):
        from unittest.mock import patch
        _, result = self.command("product",self.fields())
        with patch("affiliate_control.discovery.search",return_value=[]) as search:
            self.command("search",{"product_id":result["product_id"]})
        self.assertEqual(search.call_args.args[0]["query"],"áo khoác phối đồ")

    def test_reference_urls_no_download_or_privilege_from_provider_label(self):
        self.assertEqual(provider(normalize("https://www.tiktok.com/@owner/video/1234567890123456")),"TikTok")
        self.assertEqual(provider(normalize("https://www.instagram.com/reel/abcDef1/")),"Instagram")
        self.assertEqual(provider(normalize("https://www.facebook.com/reel/123456789")),"Facebook")
        self.assertEqual(provider("https://eviltiktok.com/file"),"eviltiktok.com")
        for url in ("https://localhost/video","https://192.168.1.1/video","https://host.internal/file","https://www.tiktok.com/",
                    "https://www.instagram.com/u/owner","https://example.org/","https://user:pass@example.org/video"):
            with self.assertRaises(ValueError):
                normalize(url)

    def report(self, **changes):
        return {"period_start":"2026-01-01","period_end":"2026-01-02","report_reference":"Owner report",
                "clicks":None,"pending_orders":1,"approved_orders":0,"approved_commission":0,"paid_amount":None,**changes}

    def test_report_unknown_zero_and_duplicate_period_not_added(self):
        self.command("affiliate_report",self.report())
        self.command("affiliate_report",self.report(clicks=7))
        report = self.app.store.read()["affiliate_reports"]
        self.assertEqual(len(report),1)
        self.assertIsNone(report[0]["paid_amount"])
        self.assertEqual(report[0]["approved_commission"],0)
        self.assertEqual(report[0]["source"],"owner_report_not_api_verified")
        for changes in ({"clicks":-1},{"clicks":True},{"pending_orders":1.5},{"approved_commission":float("inf")},
                        {"period_end":"2000-01-01"},{"product_id":"other"}):
            with self.assertRaises(ValueError):
                self.command("affiliate_report",self.report(**changes))

    def test_source_for_other_product_cannot_enter_batch(self):
        batch = self.batch()
        _, product = self.command("product",self.fields())
        _, source = self.command("source",{"product_id":product["product_id"],"title":"Áo","url":"https://example.org/video/1"})
        with self.assertRaises(ValueError):
            self.command("select",{"source_id":source["source_id"]},"selected",batch)

    def test_dashboard_estimates_do_not_imply_approved_or_paid(self):
        self.command("affiliate_report", self.report(total_orders=0, estimated_commission=0,
                     pending_orders=None, approved_orders=None, approved_commission=None))
        report = self.app.store.read()["affiliate_reports"][0]
        self.assertEqual(report["estimated_commission"], 0)
        self.assertEqual(report["total_orders"], 0)
        self.assertIsNone(report["approved_commission"])
        self.assertIsNone(report["paid_amount"])

    def test_reuse_confirmation_requires_current_asset_hash(self):
        first, source = self.batch(), self.source()
        self.command("select", {"source_id": source}, "selected", first)
        self.command("confirm", {"media_audio": True}, "selected", first)
        def changed_asset(state):
            state["sources"][0]["asset"] = {"sha256": "new-file"}
            return {}
        self.app.store.system_update(changed_asset)
        second = self.batch()
        self.command("select", {"source_id": source}, "selected", second)
        self.assertIsNone(self.app.store.read()["batches"][-1]["branches"]["selected"]["confirmation"])
