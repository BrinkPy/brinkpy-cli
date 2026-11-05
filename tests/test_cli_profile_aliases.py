import sys
import types
import unittest
from unittest.mock import patch

from typer.testing import CliRunner

# Keep imports resilient in minimal test environments.
if "jwt" not in sys.modules:
    sys.modules["jwt"] = types.ModuleType("jwt")

if "filedialpy" not in sys.modules:
    filedialpy = types.ModuleType("filedialpy")
    filedialpy.openFile = lambda **kwargs: None
    sys.modules["filedialpy"] = filedialpy

from brinkpy.brinkpy import app


class TestProfileCreateAlias(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_create_runs_new(self):
        with (
            patch("brinkpy.brinkpy.ensure_runtime_dirs"),
            patch("brinkpy.brinkpy.save_yaml_profile") as save_mock,
            patch("brinkpy.brinkpy.get_profiles_dir") as dir_mock,
        ):
            dir_mock.return_value.glob.return_value = []
            result = self.runner.invoke(app, ["profile", "create", "test1"])

        self.assertEqual(result.exit_code, 0, result.output)
        save_mock.assert_called_once_with("test1", "User-defined profile", False)

    def test_create_is_hidden_from_help(self):
        with patch("brinkpy.brinkpy.ensure_runtime_dirs"):
            result = self.runner.invoke(app, ["profile", "--help"])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("new", result.output)
        self.assertNotIn("create", result.output.replace("Create a new", ""))


if __name__ == "__main__":
    unittest.main()
