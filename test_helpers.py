"""Tests for core helper functions."""
import html
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch


class TestHtmlEscape(unittest.TestCase):
    """Verify that html.escape is applied correctly to user-controlled data."""

    XSS_PAYLOADS = [
        "<script>alert(1)</script>",
        '<img src=x onerror="alert(1)">',
        "'; DROP TABLE users; --",
        "<b>bold</b>",
        '"quoted"',
        "&ampersand",
    ]

    def test_escape_leaves_safe_strings_readable(self):
        safe = "Hello, World!"
        self.assertEqual(html.escape(safe), safe)

    def test_escape_neutralises_xss_payloads(self):
        for payload in self.XSS_PAYLOADS:
            escaped = html.escape(payload)
            self.assertNotIn("<script", escaped)
            self.assertNotIn("<img", escaped)
            self.assertNotIn("<b>", escaped)

    def test_escape_angle_brackets(self):
        self.assertIn("&lt;", html.escape("<"))
        self.assertIn("&gt;", html.escape(">"))

    def test_escape_quotes(self):
        # html.escape with quote=True (default) escapes double-quotes
        self.assertIn("&quot;", html.escape('"hello"'))


class TestAiHelperBackendKey(unittest.TestCase):
    """Test backend_to_key mapping logic."""

    def setUp(self):
        # Import here so module-level side-effects (dotenv load) are isolated
        from ai_helper import backend_to_key
        self.backend_to_key = backend_to_key

    def test_ollama_key(self):
        self.assertEqual(self.backend_to_key("Ollama (Local)"), "ollama")

    def test_claude_key(self):
        self.assertEqual(self.backend_to_key("Claude (Anthropic)"), "claude")

    def test_chatgpt_key(self):
        self.assertEqual(self.backend_to_key("ChatGPT (OpenAI)"), "chatgpt")

    def test_grok_key(self):
        self.assertEqual(self.backend_to_key("Grok (xAI)"), "grok")

    def test_unknown_defaults_to_ollama(self):
        self.assertEqual(self.backend_to_key("Unknown Backend"), "ollama")


class TestGetAvailableBackends(unittest.TestCase):
    """Test get_available_backends under various key/connection scenarios."""

    def setUp(self):
        from ai_helper import get_available_backends
        self.get_available_backends = get_available_backends

    @patch("ai_helper.check_ollama_connection", return_value=False)
    def test_no_keys_no_ollama_returns_ollama_fallback(self, _mock):
        backends = self.get_available_backends()
        self.assertEqual(backends, ["Ollama (Local)"])

    @patch("ai_helper.check_ollama_connection", return_value=True)
    def test_ollama_online_included(self, _mock):
        backends = self.get_available_backends()
        self.assertIn("Ollama (Local)", backends)

    @patch("ai_helper.check_ollama_connection", return_value=False)
    def test_claude_key_adds_claude(self, _mock):
        backends = self.get_available_backends(claude_key=True)
        self.assertIn("Claude (Anthropic)", backends)

    @patch("ai_helper.check_ollama_connection", return_value=False)
    def test_openai_key_adds_chatgpt(self, _mock):
        backends = self.get_available_backends(openai_key=True)
        self.assertIn("ChatGPT (OpenAI)", backends)

    @patch("ai_helper.check_ollama_connection", return_value=False)
    def test_grok_key_adds_grok(self, _mock):
        backends = self.get_available_backends(grok_key=True)
        self.assertIn("Grok (xAI)", backends)

    @patch("ai_helper.check_ollama_connection", return_value=False)
    def test_all_keys_all_backends(self, _mock):
        backends = self.get_available_backends(claude_key=True, grok_key=True, openai_key=True)
        self.assertIn("Claude (Anthropic)", backends)
        self.assertIn("ChatGPT (OpenAI)", backends)
        self.assertIn("Grok (xAI)", backends)


class TestGenerateResponseRouting(unittest.TestCase):
    """Test that generate_response routes to the right backend."""

    def setUp(self):
        from ai_helper import generate_response
        self.generate_response = generate_response

    def test_unknown_backend_yields_error(self):
        chunks = list(self.generate_response([], backend="unknown_backend"))
        self.assertTrue(any("Unknown backend" in c for c in chunks))

    def test_claude_without_key_yields_error(self):
        chunks = list(self.generate_response([], backend="claude", api_key=None))
        self.assertTrue(any("API key" in c for c in chunks))

    def test_chatgpt_without_key_yields_error(self):
        chunks = list(self.generate_response([], backend="chatgpt", api_key=None))
        self.assertTrue(any("API key" in c for c in chunks))

    def test_grok_without_key_yields_error(self):
        chunks = list(self.generate_response([], backend="grok", api_key=None))
        self.assertTrue(any("API key" in c for c in chunks))


class TestAssistantPersistence(unittest.TestCase):
    """Test assistant load/save round-trip using temp files."""

    def _load(self, path):
        if not os.path.exists(path):
            return []
        with open(path) as f:
            return json.load(f)

    def _save(self, path, data):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def test_roundtrip(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as tmp:
            tmp.write("[]")
            path = tmp.name

        try:
            assistant = {
                "id": "test-id",
                "name": "Test Bot",
                "description": "A test assistant",
                "system_prompt": "Be helpful.",
                "status": "Active",
                "created_at": "2026-01-01T00:00:00",
            }
            self._save(path, [assistant])
            loaded = self._load(path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["name"], "Test Bot")
            self.assertEqual(loaded[0]["system_prompt"], "Be helpful.")
        finally:
            os.unlink(path)

    def test_empty_file_returns_empty_list(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as tmp:
            tmp.write("[]")
            path = tmp.name
        try:
            loaded = self._load(path)
            self.assertEqual(loaded, [])
        finally:
            os.unlink(path)

    def test_missing_file_returns_empty_list(self):
        loaded = self._load("/tmp/does_not_exist_abc123.json")
        self.assertEqual(loaded, [])


if __name__ == "__main__":
    unittest.main()
