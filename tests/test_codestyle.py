# Style check
import unittest
import pycodestyle

class Test_Code_Format(unittest.TestCase):
    """Pep-8 check"""

    def test_conformance(self):
        """Check style"""
        # W291 is trailing whitespace, E702 multiple statements in 1 line
        # E741 ambiguous variable name
        # W293 blank line contains whitespace]
        # E226 missing whitespace around arithmetic operator

        style = pycodestyle.StyleGuide(quiet=False, ignore=['E501', 'W291', 'E702', 'E741',
                                                            'E402', 'W293', 'E226', 'E401'])
        style.input_dir('./src/audioio/')
        result = style.check_files()
        self.assertEqual(0, result.total_errors,
                         "Found code style errors (and warnings).")
