from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import uuid

from affiliate_control.connections import Connections, TOOLS
from affiliate_control.config import Settings
from affiliate_control.post_deletion import delete
import test_content as fixtures


class ConnectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.connections = Connections(Settings(state=Path(self.temp.name)))

    def test_saved_secret_never_returned_to_console_metadata(self):
        with patch.object(self.connections,"secret",return_value=None) as vault:
            result = self.connections.save({"tool":"youtube_search","value":"unit-only-placeholder"})
        vault.assert_called_once_with("save","youtube_search","unit-only-placeholder")
        self.assertNotIn("placeholder",str(result) + str(self.connections.overview()))
        self.assertTrue(self.connections.has("youtube_search"))
        with patch.object(self.connections,"secret",return_value=None):
            self.connections.remove({"tool":"youtube_search"})
        self.assertFalse(self.connections.has("youtube_search"))

    def test_unknown_tool_and_bad_body_cannot_reach_vault(self):
        with patch.object(self.connections,"secret") as vault:
            for data in ({"tool":"unknown","value":"x"},{"tool":"youtube","value":"x","path":"/tmp"},{"tool":"youtube","value":"a\nb"}):
                with self.assertRaises(ValueError):
                    self.connections.save(data)
        vault.assert_not_called()

    def test_chrome_fixed_urls_private_profile_no_cookie_export(self):
        with patch("affiliate_control.connections.CHROME",Mock(is_file=Mock(return_value=True))),patch("affiliate_control.connections.subprocess.Popen") as launch:
            result = self.connections.launch({"tool":"flow"})
        args = launch.call_args.args[0]
        self.assertEqual(args[-1],TOOLS["flow"][1])
        self.assertIn("--user-data-dir=" + str((Path(self.temp.name)/"browser-profiles/flow").resolve()),args)
        self.assertFalse(result["logged_in_verified"])
        self.assertEqual((Path(self.temp.name)/"browser-profiles/flow").stat().st_mode & 0o777,0o700)
        with self.assertRaises(ValueError):
            self.connections.launch({"tool":"flow","url":"https://evil.test"})


class DeletionTests(unittest.TestCase):
    setUp = fixtures.ContentTests.setUp
    command = fixtures.ContentTests.command

    def fake(self):
        app = Mock(content=self.app,connections=Mock())
        app.bridge.snapshot.return_value = {"videos":[{"video_id":"abcdefghijk"}]}
        app.connections.secret.return_value = "test-placeholder"
        body = {"video_id":"abcdefghijk","confirm_id":"abcdefghijk","permanent":True,
                "expected_version":self.app.store.read()["version"],"idempotency_key":str(uuid.uuid4())}
        responses = [{"items":[{"id":"channel","snippet":{"customUrl":"@chungthuyao7335"}}]},
                     {"items":[{"snippet":{"channelId":"channel"}}]},True]
        return app,body,responses

    def test_delete_checks_owner_reserves_and_does_not_repeat(self):
        app,body,responses = self.fake()
        with patch("affiliate_control.post_deletion.call",side_effect=responses) as api:
            result = delete(app,body)
            delete(app,body)
        self.assertEqual(api.call_count,3)
        self.assertEqual(result["deletion"],"deleted_on_youtube")
        with self.assertRaises(ValueError):
            self.command("post_control",{"video_id":body["video_id"],"choice":"cancel_delete"})

    def test_wrong_channel_unknown_id_and_no_confirmation_never_delete(self):
        for change in ({"video_id":"unknown0000","confirm_id":"unknown0000"},{"permanent":False},{"confirm_id":"wrong"}):
            app,body,_ = self.fake()
            with patch("affiliate_control.post_deletion.call") as api,self.assertRaises(ValueError):
                delete(app,body | change)
            api.assert_not_called()
        app,body,responses = self.fake()
        responses[1]["items"][0]["snippet"]["channelId"] = "other"
        with patch("affiliate_control.post_deletion.call",side_effect=responses) as api,self.assertRaises(ValueError):
            delete(app,body)
        self.assertEqual(api.call_count,2)

    def test_timeout_records_uncertain_and_blocks_blind_retry(self):
        app,body,responses = self.fake()
        with patch("affiliate_control.post_deletion.call",side_effect=responses[:2]+[TimeoutError()]):
            self.assertEqual(delete(app,body)["deletion"],"uncertain")
        with patch("affiliate_control.post_deletion.call") as api,self.assertRaises(ValueError):
            delete(app,body | {"expected_version":self.app.store.read()["version"],"idempotency_key":str(uuid.uuid4())})
        api.assert_not_called()

    def test_hide_and_request_are_not_platform_delete(self):
        self.command("post_control",{"video_id":"abcdefghijk","choice":"hide"})
        self.command("post_control",{"video_id":"abcdefghijk","choice":"request_delete","confirm_id":"abcdefghijk"})
        row = self.app.store.read()["publication_controls"]["abcdefghijk"]
        self.assertTrue(row["hidden"])
        self.assertEqual(row["deletion"],"requested_not_deleted")
