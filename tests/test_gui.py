import unittest
from audioio.gui import App


class TestApp(unittest.TestCase):
    """Test App class in gui"""

    def test_version_check(self):
        """Print out pyqt5 version"""
        a = App()
        a.checkqt()

    def test_wrong_aio_type(self):
        """If aio is not Audioio class, raise error"""
        with self.assertRaises(TypeError):
            a = App(aio=4)

