from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from affiliate_control import created_renderer


class CreatedRendererTests(unittest.TestCase):
    def test_missing_tools_disable_renderer(self):
        self.assertFalse(created_renderer.available(None))
        with tempfile.TemporaryDirectory() as folder:
            self.assertFalse(created_renderer.available(Path(folder)))

    def test_known_product_plan_is_five_scenes_not_provider_claims(self):
        scenes = created_renderer.scene_plan({"shop_id": "928446709", "item_id": "24035184620"})
        self.assertEqual(len(scenes), 5)
        self.assertIn("hồ sơ", scenes[-1]["voice"])
        self.assertTrue(all(len(s["voice"]) <= 180 for s in scenes))

    def test_wrong_sku_cannot_reuse_m31_graphics_even_with_script(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(created_renderer, "available", return_value=True):
            with self.assertRaises(ValueError):
                created_renderer.render(Path(folder), Path(folder), {"product": {"shop_id": "other", "item_id": "other"}},
                                        {"run_id": "test", "scenes": [{"voice": "test"}]}, lambda _: None)
