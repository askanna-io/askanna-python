import datetime
import unittest

from askanna.core.utils import translate_dtype


class DtypeConverterTest(unittest.TestCase):
    def test_translate_dtype(self):
        self.assertEqual(translate_dtype(True), "boolean")
        self.assertEqual(translate_dtype(False), "boolean")

        self.assertEqual(translate_dtype("0"), "string")
        self.assertEqual(translate_dtype("some text"), "string")

        self.assertEqual(translate_dtype(0), "integer")
        self.assertEqual(translate_dtype(10), "integer")

        self.assertEqual(translate_dtype(3.14), "float")
        self.assertEqual(translate_dtype(5.0), "float")

        self.assertEqual(translate_dtype({"test": True}), "dictionary")

        self.assertEqual(translate_dtype(datetime.date(2021, 4, 9)), "date")
        self.assertEqual(translate_dtype(datetime.time(hour=0)), "time")
        self.assertEqual(translate_dtype(datetime.datetime.now()), "datetime")
