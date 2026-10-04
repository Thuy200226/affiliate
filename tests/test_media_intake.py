from copy import deepcopy
from http.client import HTTPConnection
import hashlib
import json
import uuid
import unittest
from unittest.mock import patch

from affiliate_control.content_initial import initial
from affiliate_control.uploads import attach
from affiliate_domain.two_video import new_batch, select_source, confirm_source
import test_http as fixtures


class IntakeTests(unittest.TestCase):
    setUp = fixtures.HTTPTests.setUp
    tearDown = fixtures.HTTPTests.tearDown
    request = fixtures.HTTPTests.request

    def seed(self):
        ident = str(uuid.uuid4())
        def data(state):
            state.update(initial(self.app.settings.state))
            state["sources"].append({"id":ident,"product_id":"m31","url":"https://example.org/video","title":"Clip","creator":"Owner"})
            return {}
        self.app.content.store.system_update(data)
        return ident

    def test_binary_upload_session_csrf_header_limit_and_source_preview(self):
        ident = self.seed()
        payload = b"\x00\x00\x00\x18ftypmp42" + b"0" * 32
        headers = self.headers | {"Content-Type":"video/mp4","X-Media-Target":"source","X-Media-Id":ident,
                                  "X-Workspace-Version":str(self.app.content.store.read()["version"])}
        self.assertEqual(self.request("POST","/api/content/upload",payload,{})[0],403)
        digest = hashlib.sha256(payload).hexdigest()
        artifact = {"sha256":digest,"duration_seconds":8,"width":1080,"height":1920,"technical_passed":True}
        with patch("affiliate_control.uploads.inspect",return_value=artifact):
            status,_,body = self.request("POST","/api/content/upload",payload,headers)
        self.assertEqual(status,200)
        self.assertEqual(json.loads(body)["source_id"],ident)
        status,_,part = self.request("GET","/api/content/source-media/"+ident,headers=self.headers | {"Range":"bytes=4-7"})
        self.assertEqual((status,part),(206,b"ftyp"))
        self.assertEqual(self.request("POST","/api/content/upload",payload,headers)[0],409)

    def test_invalid_mp4_and_oversized_upload_not_attached(self):
        ident = self.seed()
        headers = self.headers | {"Content-Type":"video/mp4","X-Media-Target":"source","X-Media-Id":ident,
                                  "X-Workspace-Version":str(self.app.content.store.read()["version"])}
        self.assertEqual(self.request("POST","/api/content/upload",b"not-a-video" * 3,headers)[0],400)
        with patch("affiliate_control.uploads.inspect") as inspect:
            self.assertEqual(self.request("POST","/api/content/upload",b"",headers | {"Content-Length":str(101*1024*1024)})[0],400)
        inspect.assert_not_called()
        self.assertNotIn("asset",self.app.content.store.read()["sources"][0])

    def test_received_source_changes_only_matching_selected_revision(self):
        state = initial(self.app.settings.state)
        source = {"id":"one","product_id":"m31","url":"https://example.org/video"}
        state["sources"].append(source); batch = new_batch(state["products"][0],{}); state["batches"].append(batch)
        select_source(batch,source); created = deepcopy(batch["branches"]["created"])
        confirm_source(batch["branches"]["selected"],source,{"media_audio":True})
        attach(state,"source","one",{"sha256":"hash"})
        self.assertIsNone(batch["branches"]["selected"]["confirmation"])
        self.assertEqual(batch["branches"]["created"],created)

    def test_processed_file_needs_matching_real_asset_confirmation(self):
        state = initial(self.app.settings.state)
        source = {"id":"one","product_id":"m31","url":"https://example.org/video","asset":{"sha256":"original"}}
        state["sources"].append(source); batch = new_batch(state["products"][0],{}); state["batches"].append(batch)
        select_source(batch,source); branch = batch["branches"]["selected"]
        with self.assertRaises(ValueError):
            attach(state,"selected",batch["id"],{"sha256":"output"})
        confirm_source(branch,source,{"media_audio":True})
        self.assertEqual(branch["confirmation"]["asset_hash"],"original")
        result = attach(state,"selected",batch["id"],{"sha256":"output","perceptual_reviewed":False})
        self.assertEqual(branch["status"],"ready")
        self.assertEqual(result["kind"],"selected")
        self.assertFalse(branch["artifact"]["perceptual_reviewed"])
