import os
import json
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from clientmytcc.session import save_session, load_session, clear_session, get_session_path, Session
from clientmytcc.client import Client

class TestSessionManagement(unittest.TestCase):
    def setUp(self):
        # Ensure we don't overwrite actual user session
        self.original_home = Path.home()
        self.test_home = Path("/tmp/test_home")
        self.test_home.mkdir(parents=True, exist_ok=True)
        
        # Patch Path.home to return our test home
        self.patcher = patch("pathlib.Path.home", return_value=self.test_home)
        self.mock_home = self.patcher.start()
        
    def tearDown(self):
        self.patcher.stop()
        # Clean up
        import shutil
        if self.test_home.exists():
            shutil.rmtree(self.test_home)

    def test_save_and_load_session(self):
        email = "test@example.com"
        cookies = {"session_id": "12345", "auth": "token"}
        
        save_session(email, cookies)
        
        session_path = get_session_path()
        self.assertTrue(session_path.exists())
        
        loaded_session = load_session()
        self.assertIsNotNone(loaded_session)
        self.assertEqual(loaded_session.email, email)
        
        # Verify cookies are stored as list of strings
        self.assertIsInstance(loaded_session.cookies, list)
        self.assertIn("session_id=12345", loaded_session.cookies)
        self.assertIn("auth=token", loaded_session.cookies)

    def test_cookies_to_dict(self):
        from clientmytcc.session import cookies_to_dict
        cookie_list = ["session_id=12345", "auth=token", "complex=val; Path=/"]
        cookies = cookies_to_dict(cookie_list)
        
        self.assertEqual(cookies["session_id"], "12345")
        self.assertEqual(cookies["auth"], "token")
        self.assertEqual(cookies["complex"], "val")

    def test_clear_session(self):
        email = "test@example.com"
        cookies = {"session_id": "12345"}
        save_session(email, cookies)
        
        self.assertTrue(get_session_path().exists())
        
        clear_session()
        
        self.assertFalse(get_session_path().exists())
        self.assertIsNone(load_session())

    def test_client_initialization_with_cookies(self):
        cookies = {"session_id": "12345"}
        client = Client(cookies=cookies)
        
        self.assertTrue(client._authenticated)
        self.assertEqual(client.cookies, cookies)
        self.assertEqual(client.session.cookies.get("session_id"), "12345")

    def test_client_initialization_without_cookies(self):
        client = Client()
        self.assertFalse(client._authenticated)
        self.assertEqual(client.cookies, {})

if __name__ == "__main__":
    unittest.main()
