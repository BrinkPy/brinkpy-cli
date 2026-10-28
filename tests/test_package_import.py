import unittest

class TestBrinkpyPackageImport(unittest.TestCase):
    def test_import_and_main_exposed(self):
        import brinkpy
        self.assertTrue(hasattr(brinkpy, "main"), "brinkpy should expose main in __init__")

if __name__ == "__main__":
    unittest.main()
