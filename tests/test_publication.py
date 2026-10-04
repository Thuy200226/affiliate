from dataclasses import replace
from datetime import datetime, timedelta, timezone
import unittest

from affiliate_domain.publication import Product, LinkEvidence, build_post


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)
        self.product = Product("shop1", "item1", "variant-usbc", "Micro cài áo")
        self.link = LinkEvidence("https://s.shopee.vn/example", "owner", "shop1", "item1",
                                 "variant-usbc", "channel", "youtube_shorts", "profile",
                                 "local-proof-1", self.now + timedelta(hours=1))

    def post(self, evidence=None, **changes):
        return build_post(self.product, evidence or self.link, changes.get("owner", "owner"),
                          "channel", ["#micro", "#congnghe", "#micro"], self.now)

    def test_short_uses_profile_route_not_description_url(self):
        post = self.post()
        self.assertNotIn("https:", post["cta"])
        self.assertEqual(post["link"], self.link.url)
        self.assertEqual(post["hashtags"], ["#micro", "#congnghe"])

    def test_wrong_product_variant_owner_or_destination_rejected(self):
        for change in ({"item_id": "other"}, {"variant_id": "other"},
                       {"affiliate_account_id": "other"}, {"target_account_id": "other"},
                       {"url": "https://s.shopee.vn.attacker.example/x"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.post(replace(self.link, **change))

    def test_stale_evidence_and_nonclickable_placement_rejected(self):
        with self.assertRaises(ValueError):
            self.post(replace(self.link, expires_at=self.now - timedelta(seconds=1)))
        with self.assertRaises(ValueError):
            self.post(replace(self.link, placement="description"))

    def test_long_video_preserves_exact_owned_link(self):
        post = self.post(replace(self.link, platform="youtube_long", placement="description"))
        self.assertIn(self.link.url, post["cta"])
