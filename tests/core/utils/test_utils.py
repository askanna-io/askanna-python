import datetime
import unittest

from askanna.core.utils import translate_dtype, validate_value, update_available


class TestValidateValue(unittest.TestCase):
    def test_translate_dtype(self):
        self.assertTrue(validate_value(True))
        self.assertTrue(validate_value(False))

        self.assertTrue(validate_value("0"))
        self.assertTrue(validate_value("some text"))

        self.assertTrue(validate_value(0))
        self.assertTrue(translate_dtype(10))

        self.assertTrue(validate_value(3.14))
        self.assertTrue(validate_value(5.0))

        self.assertTrue(validate_value(["test", "some text"]))
        self.assertTrue(validate_value({"test": True}))

        self.assertTrue(validate_value(datetime.date(2021, 4, 9)))
        self.assertTrue(validate_value(datetime.time(hour=0)))
        self.assertTrue(validate_value(datetime.datetime.now()))


class TestTranslateDtype(unittest.TestCase):
    def test_translate_dtype(self):
        self.assertEqual(translate_dtype(True), "boolean")
        self.assertEqual(translate_dtype(False), "boolean")

        self.assertEqual(translate_dtype("0"), "string")
        self.assertEqual(translate_dtype("some text"), "string")

        self.assertEqual(translate_dtype(0), "integer")
        self.assertEqual(translate_dtype(10), "integer")

        self.assertEqual(translate_dtype(3.14), "float")
        self.assertEqual(translate_dtype(5.0), "float")

        self.assertEqual(translate_dtype(["test", "some text"]), "list")
        self.assertEqual(translate_dtype({"test": True}), "dictionary")

        self.assertEqual(translate_dtype(datetime.date(2021, 4, 9)), "date")
        self.assertEqual(translate_dtype(datetime.time(hour=0)), "time")
        self.assertEqual(translate_dtype(datetime.datetime.now()), "datetime")


class TestUpdateAvailable(unittest.TestCase):
    def test_update_available(self):
        self.assertIn(update_available(), [True, False])
