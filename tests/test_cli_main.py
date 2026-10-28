import unittest
import importlib

class TestBrinkpyCliMain(unittest.TestCase):
    def test_main_module_imports(self):
        # Ensure __main__ imports without triggering execution
        mod = importlib.import_module('brinkpy.__main__')
        self.assertTrue(hasattr(mod, '__name__'))

    def test_entrypoint_callable(self):
        # Ensure brinkpy.main exists and is callable
        from brinkpy import main
        self.assertTrue(callable(main))

if __name__ == "__main__":
    unittest.main()
