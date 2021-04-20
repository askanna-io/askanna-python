import unittest

from askanna.core import utils


class UtilsTest(unittest.TestCase):
    def test_extract_pushtarget_notset(self):
        with self.assertRaises(ValueError):
            utils.extract_push_target("")
