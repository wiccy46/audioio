import unittest
import pycodestyle


class TestCodeFormat(unittest.TestCase):

    def test_conformance(self):
        """Test that we conform to PEP-8."""
        # W291 is trailing whitespace, E702 multiple statements in 1 line
        # E741 ambiguous variable name
        # W293 blank line contains whitespace
        style = pycodestyle.StyleGuide(quiet=False, ignore=['E501', 'W291', 'E702', 'E741', 'W293'])
        style.input_dir('../../pysoundrefiner/')
        result = style.check_files()
        self.assertEqual(0, result.total_errors,
                         "Found code style errors (and warnings).")
