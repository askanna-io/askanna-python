import datetime
import sys
import unittest

from askanna.core.utils import (
    prepare_and_validate_value,
    translate_dtype,
    transform_value,
    update_available,
    validate_value,
)

if sys.version_info.minor < 10:
    import numpy as np


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

        if sys.version_info.minor < 10:
            self.assertTrue(validate_value(np.float(5.21)))

        self.assertTrue(validate_value(["test", "some text"]))
        self.assertTrue(validate_value({"test": True}))

        self.assertTrue(validate_value(datetime.date(2021, 4, 9)))
        self.assertTrue(validate_value(datetime.time(hour=0)))
        self.assertTrue(validate_value(datetime.datetime.now()))

        self.assertFalse(validate_value(range(0, 10)))


class TestPrepareAndValidateValue(unittest.TestCase):
    def test_prepare_and_validate_value_string(self):
        value, valid = prepare_and_validate_value("some text")
        self.assertEqual(value, "some text")
        self.assertTrue(valid)

    def test_prepare_and_validate_value_range(self):
        value, valid = prepare_and_validate_value(range(0, 3))
        self.assertEqual(value, [0, 1, 2])
        self.assertTrue(valid)

    @unittest.skipIf(sys.version_info.minor > 9, "Numpy doesn't work in Python 3.10")
    def test_prepare_and_validate_value_numpy_float(self):
        value, valid = prepare_and_validate_value(np.float(5.21))
        self.assertEqual(value, 5.21)
        self.assertTrue(valid)


class TestTransformValue(unittest.TestCase):
    def test_transform_value_string(self):
        value, transform = transform_value("some text")
        self.assertEqual(value, "some text")
        self.assertFalse(transform)

    def test_transform_value_range(self):
        value, transform = transform_value(range(0, 3))
        self.assertEqual(value, [0, 1, 2])
        self.assertTrue(transform)

    @unittest.skipIf(sys.version_info.minor > 9, "Numpy doesn't work in Python 3.10")
    def test_transform_value_numpy_float(self):
        value, transform = transform_value(np.float(5.21))
        self.assertEqual(value, 5.21)
        self.assertFalse(transform)


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
