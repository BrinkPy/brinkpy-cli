# Copyright by Dr. Cesar Carrasco, (2025)
"""The CLI copy of data_models.py must match the API copy, which is the source of truth."""

import os
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLI_FILE = REPO / "brinkpy" / "config" / "data_models.py"
API_FILE = Path(os.getenv("BRINKPY_API_DIR", REPO.parent / "brinkpy-api")) / "src" / "config" / "data_models.py"
HEADER = (
    "# Generated from brinkpy-api/src/config/data_models.py by scripts/sync_data_models.sh. Do not edit by hand."
)


class test_data_models_sync(unittest.TestCase):
    def test_header_marks_the_file_as_generated(self):
        first_line = CLI_FILE.read_text(encoding="utf-8").split("\n", 1)[0]
        self.assertEqual(first_line, HEADER, "Run scripts/sync_data_models.sh to regenerate the CLI copy.")

    @unittest.skipUnless(API_FILE.is_file(), f"API copy not found at {API_FILE}")
    def test_matches_api_copy(self):
        cli_body = CLI_FILE.read_text(encoding="utf-8").split("\n", 1)[1]
        self.assertTrue(
            cli_body == API_FILE.read_text(encoding="utf-8"),
            "brinkpy/config/data_models.py differs from the API copy. "
            "Edit the API copy, then run scripts/sync_data_models.sh.",
        )


if __name__ == "__main__":
    unittest.main()
