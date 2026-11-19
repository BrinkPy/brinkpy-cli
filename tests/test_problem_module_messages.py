"""
Tests for the messages load_problem_from_module prints when the problem module can't be loaded: they point to the
line of the user's module and leave out the CLI's own code.
"""

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from brinkpy.utils import api_utils


class ProblemModuleMessageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def load(self, source: str) -> str:
        path = Path(self.tmp.name) / "UserProblem.py"
        path.write_text(textwrap.dedent(source))
        with patch.object(api_utils.console, "print") as printed:
            problem = api_utils.load_problem_from_module(path)
        self.assertIsNone(problem)
        self.assertEqual(printed.call_count, 1)
        message = printed.call_args.args[0]
        self.assertNotIn("api_utils.py", message)
        self.assertNotIn("importlib", message)
        return message

    def test_syntax_error(self):
        message = self.load(
            """
            def Problem():
                return {"name": "x"
            """
        )
        self.assertIn("SyntaxError: '{' was never closed. In your problem module: line 3: return {\"name\": \"x\"", message)

    def test_missing_problem_function(self):
        message = self.load(
            """
            def problem_definition():
                return {}
            """
        )
        self.assertIn("The problem module UserProblem.py does not define a Problem() (or problem()) function.", message)

    def test_error_in_helper_shows_the_calling_line(self):
        message = self.load(
            """
            def helper():
                raise ValueError("bad value")


            def Problem():
                return {"m": helper()}
            """
        )
        self.assertIn(
            'ValueError: bad value. In your problem module: line 3, in helper: raise ValueError("bad value"); '
            'called from line 7, in Problem: return {"m": helper()}',
            message,
        )

    def test_library_error_names_the_library(self):
        message = self.load(
            """
            import numpy as np


            def Problem():
                return {"m": np.linalg.inv(np.zeros((2, 2)))}
            """
        )
        self.assertIn("LinAlgError: Singular matrix. Raised in numpy, called from your problem module: line 6, in Problem", message)

    def test_top_level_error(self):
        message = self.load(
            """
            SCALE = LIMIT * 2


            def Problem():
                return {}
            """
        )
        self.assertIn("NameError: name 'LIMIT' is not defined. In your problem module: line 2: SCALE = LIMIT * 2", message)

    def test_valid_module_returns_the_problem(self):
        path = Path(self.tmp.name) / "GoodProblem.py"
        path.write_text("def Problem():\n    return {'name': 'good'}\n")
        with patch.object(api_utils.console, "print") as printed:
            problem = api_utils.load_problem_from_module(path)
        self.assertEqual(problem, {"name": "good"})
        printed.assert_not_called()


class GetExceptionSourceTests(unittest.TestCase):
    def test_without_module_only_type_and_message(self):
        try:
            raise OSError("cannot open the file.")
        except OSError as e:
            self.assertEqual(api_utils.get_exception_source(e), "OSError: cannot open the file")


if __name__ == "__main__":
    unittest.main()
