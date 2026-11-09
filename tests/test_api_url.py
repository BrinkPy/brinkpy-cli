import os
import unittest
from unittest.mock import patch

from brinkpy.utils import api_utils


class GetApiUrlTests(unittest.TestCase):
    def setUp(self):
        api_utils._api_url_notice_shown = False

    def test_default_url_without_variable(self):
        env = {k: v for k, v in os.environ.items() if k != "BRINKPY_API_URL"}
        with patch.dict(os.environ, env, clear=True), patch.object(api_utils.console, "print") as printed:
            self.assertEqual(api_utils.get_api_url(), api_utils.DEFAULT_API_URL)
        printed.assert_not_called()

    def test_empty_variable_uses_default(self):
        with patch.dict(os.environ, {"BRINKPY_API_URL": ""}), patch.object(api_utils.console, "print") as printed:
            self.assertEqual(api_utils.get_api_url(), api_utils.DEFAULT_API_URL)
        printed.assert_not_called()

    def test_override_prints_notice_once(self):
        with patch.dict(os.environ, {"BRINKPY_API_URL": "http://localhost:8080/"}), patch.object(
            api_utils.console, "print"
        ) as printed:
            self.assertEqual(api_utils.get_api_url(), "http://localhost:8080")
            self.assertEqual(api_utils.get_api_url(), "http://localhost:8080")
        printed.assert_called_once()
        self.assertIn("Using API at http://localhost:8080", printed.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
