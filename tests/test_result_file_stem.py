import unittest

from brinkpy.utils.api_utils import result_file_stem


class TestResultFileStem(unittest.TestCase):
    def test_spaces_and_dots_become_underscores(self):
        problem_json = {"name": "Sorensen 8.1", "Request_ID": "725856734eb54e3a99d786d3f05e70c6"}
        self.assertEqual(result_file_stem(problem_json), "Sorensen_8_1-e70c6")

    def test_slashes_and_colons_become_underscores(self):
        problem_json = {"name": "Load/Resistance: Case 1", "Request_ID": "725856734eb54e3a99d786d3f05e70c6"}
        self.assertEqual(result_file_stem(problem_json), "Load_Resistance__Case_1-e70c6")

    def test_plain_name_unchanged(self):
        problem_json = {"name": "AT68", "Request_ID": "6287a42cac1148e3912a0b24b890c097"}
        self.assertEqual(result_file_stem(problem_json), "AT68-0c097")


if __name__ == "__main__":
    unittest.main()
