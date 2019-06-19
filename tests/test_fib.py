import unittest
from audioio.skeleton import fib


class TestFib(unittest.TestCase):
    """Test skeleton.py"""
    def test_fib(self):
        self.assertEqual(fib(1), 1)
        self.assertEqual(fib(2), 1)
        self.assertEqual(fib(7), 13)
