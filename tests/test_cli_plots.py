import pickle
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typer.testing import CliRunner

# Keep imports resilient in minimal test environments.
if "jwt" not in sys.modules:
    sys.modules["jwt"] = types.ModuleType("jwt")

if "filedialpy" not in sys.modules:
    filedialpy = types.ModuleType("filedialpy")
    filedialpy.openFile = lambda **kwargs: None
    sys.modules["filedialpy"] = filedialpy

from brinkpy.brinkpy import app
from brinkpy.utils.api_utils import show_figures_from_pickle


class TestPlotsCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_given_file_is_opened(self):
        with tempfile.TemporaryDirectory() as tmp:
            pickle_file = Path(tmp, "AT68-0c097.pickle")
            pickle_file.touch()
            with (
                patch("brinkpy.brinkpy.ensure_runtime_dirs"),
                patch("brinkpy.brinkpy.get_pickle_file_name") as picker_mock,
                patch("brinkpy.brinkpy.show_figures_from_pickle", return_value=True) as show_mock,
            ):
                result = self.runner.invoke(app, ["plots", str(pickle_file)])

        self.assertEqual(result.exit_code, 0, result.output)
        picker_mock.assert_not_called()
        show_mock.assert_called_once_with(pickle_file)

    def test_missing_file_exits_with_error(self):
        with (
            patch("brinkpy.brinkpy.ensure_runtime_dirs"),
            patch("brinkpy.brinkpy.show_figures_from_pickle") as show_mock,
        ):
            result = self.runner.invoke(app, ["plots", "results/missing.pickle"])

        self.assertEqual(result.exit_code, 1)
        show_mock.assert_not_called()

    def test_picker_opens_without_argument(self):
        selected = Path("results/2026-11-03/18-10-59/AT68-0c097.pickle")
        with (
            patch("brinkpy.brinkpy.ensure_runtime_dirs"),
            patch("brinkpy.brinkpy.get_pickle_file_name", return_value=selected) as picker_mock,
            patch("brinkpy.brinkpy.show_figures_from_pickle", return_value=True) as show_mock,
        ):
            result = self.runner.invoke(app, ["plots"])

        self.assertEqual(result.exit_code, 0, result.output)
        picker_mock.assert_called_once()
        show_mock.assert_called_once_with(selected)

    def test_cancelled_picker_does_nothing(self):
        with (
            patch("brinkpy.brinkpy.ensure_runtime_dirs"),
            patch("brinkpy.brinkpy.get_pickle_file_name", return_value=None),
            patch("brinkpy.brinkpy.show_figures_from_pickle") as show_mock,
        ):
            result = self.runner.invoke(app, ["plots"])

        self.assertEqual(result.exit_code, 0, result.output)
        show_mock.assert_not_called()


class TestShowFiguresFromPickle(unittest.TestCase):
    def test_list_of_figures_is_shown(self):
        figures = [plt.figure(), plt.figure()]
        with tempfile.TemporaryDirectory() as tmp:
            pickle_file = Path(tmp, "plots.pickle")
            with open(pickle_file, "wb") as f:
                pickle.dump(figures, f)
            plt.close("all")
            with patch("builtins.input", return_value=""):
                self.assertTrue(show_figures_from_pickle(pickle_file))

    def test_pickle_without_figures_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            pickle_file = Path(tmp, "plots.pickle")
            with open(pickle_file, "wb") as f:
                pickle.dump({"not": "figures"}, f)
            self.assertFalse(show_figures_from_pickle(pickle_file))


if __name__ == "__main__":
    unittest.main()
