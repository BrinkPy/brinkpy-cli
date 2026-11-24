"""
Pickled plots open reliably only with the Matplotlib minor version and NumPy major version that wrote them. The CLI
reads the versions the API recorded ("PlotVersions") and tells the user how to open the plots.
"""

import json
import pickle
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from brinkpy.utils import api_utils


def printed(mock) -> str:
    return "\n".join(str(c.args[0]) for c in mock.call_args_list if c.args)


class AdviceTests(unittest.TestCase):
    def test_same_versions_need_no_advice(self):
        same = {"matplotlib": matplotlib.__version__, "numpy": np.__version__}
        self.assertEqual(api_utils.plot_version_advice(same), [])
        self.assertEqual(api_utils.plot_version_advice(None), [])

    def test_patch_releases_are_compatible(self):
        major, minor = matplotlib.__version__.split(".")[:2]
        self.assertEqual(api_utils.plot_version_advice({"matplotlib": f"{major}.{minor}.99"}), [])

    def test_different_matplotlib_minor(self):
        advice = api_utils.plot_version_advice({"matplotlib": "3.4.1"})
        self.assertEqual(len(advice), 1)
        self.assertIn('pip install "matplotlib==3.4.*"', advice[0])

    def test_different_numpy_major(self):
        advice = api_utils.plot_version_advice({"numpy": "1.26.4"})
        self.assertEqual(len(advice), 1)
        self.assertIn('pip install "numpy>=1,<2"', advice[0])


class RecordedVersionsTests(unittest.TestCase):
    def test_from_the_results_or_the_json_next_to_the_pickle(self):
        with tempfile.TemporaryDirectory() as tmp:
            pickle_path = Path(tmp) / "Run-ab12c.pickle"
            self.assertIsNone(api_utils.recorded_plot_versions(pickle_path))
            versions = {"matplotlib": "3.11.2", "numpy": "2.5.4"}
            self.assertEqual(api_utils.recorded_plot_versions(pickle_path, {"PlotVersions": versions}), versions)
            pickle_path.with_suffix(".json").write_text(json.dumps({"PlotVersions": versions}))
            self.assertEqual(api_utils.recorded_plot_versions(pickle_path), versions)
            # Runs from before the API recorded the versions
            pickle_path.with_suffix(".json").write_text(json.dumps({"AnalysisResults": {}}))
            self.assertIsNone(api_utils.recorded_plot_versions(pickle_path))


class ShowFiguresTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pickle_path = Path(self.tmp.name) / "Run-ab12c.pickle"

    def test_unreadable_pickle_gives_guidance_not_a_traceback(self):
        self.pickle_path.write_bytes(b"not a pickle")
        self.pickle_path.with_suffix(".pdf").write_bytes(b"%PDF")
        self.pickle_path.with_suffix(".json").write_text(json.dumps({"PlotVersions": {"matplotlib": "3.4.1"}}))
        with patch.object(api_utils.console, "print") as out, patch("traceback.print_exc") as tb:
            self.assertFalse(api_utils.show_figures_from_pickle(self.pickle_path))
        text = printed(out)
        tb.assert_not_called()
        self.assertIn('matplotlib==3.4.*', text)
        self.assertIn("Could not open the plots", text)
        self.assertIn(str(self.pickle_path.with_suffix(".pdf")), text)

    def test_unreadable_pickle_without_recorded_versions(self):
        self.pickle_path.write_bytes(b"not a pickle")
        with patch.object(api_utils.console, "print") as out:
            self.assertFalse(api_utils.show_figures_from_pickle(self.pickle_path))
        self.assertIn("pip install --upgrade brinkpy", printed(out))

    def test_matching_pickle_opens(self):
        fig = plt.figure()
        plt.plot([0, 1], [0, 1])
        with open(self.pickle_path, "wb") as f:
            pickle.dump([fig], f)
        plt.close("all")
        with patch.object(api_utils.console, "print") as out, patch.object(api_utils.plt, "show"), \
                patch("builtins.input", return_value=""):
            self.assertTrue(api_utils.show_figures_from_pickle(self.pickle_path, {"PlotVersions": {
                "matplotlib": matplotlib.__version__, "numpy": np.__version__}}))
        self.assertNotIn("saved with", printed(out))


if __name__ == "__main__":
    unittest.main()
