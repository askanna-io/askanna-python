import datetime
import unittest

import numpy as np

from askanna.core.utils import (
    prepare_and_validate_value,
    transform_value,
    translate_dtype,
    update_available,
    validate_value,
    value_not_empty,
)


class TestValidateValue(unittest.TestCase):
    def test_validate_value(self):
        self.assertTrue(validate_value(True))
        self.assertTrue(validate_value(False))

        self.assertTrue(validate_value("0"))
        self.assertTrue(validate_value("some text"))

        self.assertTrue(validate_value(0))
        self.assertTrue(validate_value(10))

        self.assertTrue(validate_value(3.14))
        self.assertTrue(validate_value(5.0))

        self.assertTrue(validate_value(np.float16(5.21)))

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

    def test_prepare_and_validate_value_numpy_float(self):
        value, valid = prepare_and_validate_value(np.float16(5.21))
        self.assertEqual(value, np.float16(5.21))
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

    def test_transform_value_numpy_float(self):
        value, transform = transform_value(np.float16(5.21))
        self.assertEqual(value, np.float16(5.21))
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

        self.assertEqual(translate_dtype({"foo": "bar"}), "dictionary")
        self.assertEqual(translate_dtype({"foo": True}), "dictionary")

        self.assertEqual(translate_dtype(datetime.date(2021, 4, 9)), "date")
        self.assertEqual(translate_dtype(datetime.time(hour=0)), "time")
        self.assertEqual(translate_dtype(datetime.datetime.now()), "datetime")

        self.assertEqual(translate_dtype(range(0, 10)), "range")

        self.assertEqual(translate_dtype([0, 1]), "list_integer")
        self.assertEqual(translate_dtype([1.11, 1.12]), "list_float")
        self.assertEqual(translate_dtype([0, 1.12]), "list_float")
        self.assertEqual(translate_dtype(["foo", "bar"]), "list_string")
        self.assertEqual(translate_dtype([0, "bar"]), "list")
        self.assertEqual(translate_dtype([1.11, True]), "list")
        self.assertEqual(translate_dtype([True, False]), "list_boolean")
        self.assertEqual(translate_dtype([False, False]), "list_boolean")
        self.assertEqual(translate_dtype([True, True]), "list_boolean")
        self.assertEqual(translate_dtype([datetime.datetime.now(), datetime.datetime.now()]), "list_datetime")
        self.assertEqual(translate_dtype([datetime.time(13, 21), datetime.time(8, 9)]), "list_time")
        self.assertEqual(translate_dtype([datetime.date(2022, 12, 11), datetime.date(2022, 12, 12)]), "list_date")
        self.assertEqual(translate_dtype(np.array([0, 1])), "list_integer")
        self.assertEqual(translate_dtype(np.array([1.11, 1.12])), "list_float")
        self.assertEqual(translate_dtype(np.array(["foo", "bar"])), "list")
        self.assertEqual(translate_dtype(np.array([True, False])), "list")

        self.assertEqual(translate_dtype(np.int_(1)), "integer")
        self.assertEqual(translate_dtype(np.float16(1.11)), "float")
        self.assertEqual(translate_dtype(np.str_("foo")), "string")
        self.assertEqual(translate_dtype(np.bool_(False)), "boolean")


class TestUpdateAvailable(unittest.TestCase):
    def test_update_available(self):
        self.assertIn(update_available(), [True, False])


class TestValueNotEmpty(unittest.TestCase):
    def test_value_not_empty_string(self):
        value = "test"
        self.assertTrue(value_not_empty(value))

    def test_value_not_empty_with_empty_string(self):
        value = ""
        self.assertFalse(value_not_empty(value))

    def test_value_not_empty_with_value_none(self):
        value = None
        self.assertFalse(value_not_empty(value))

    def test_value_not_empty_with_list(self):
        value = ["foo", "bar"]
        self.assertTrue(value_not_empty(value))

    def test_value_not_empty_with_empty_list(self):
        value = []
        self.assertFalse(value_not_empty(value))

    def test_value_not_empty_with_dict(self):
        value = {"foo": "bar"}
        self.assertTrue(value_not_empty(value))

    def test_value_not_empty_with_empty_dict(self):
        value = {}
        self.assertFalse(value_not_empty(value))

    def test_value_not_empty_with_integer(self):
        value = int(1)
        self.assertTrue(value_not_empty(value))

    def test_value_not_empty_with_float(self):
        value = float(1.11)
        self.assertTrue(value_not_empty(value))

    def test_value_not_empty_with_bool(self):
        value = bool(False)
        self.assertTrue(value_not_empty(value))

        value = bool(True)
        self.assertTrue(value_not_empty(value))

    def test_value_not_empty_with_numpy(self):
        value = np.float16(1.11)
        self.assertTrue(value_not_empty(value))

        if np.__version__ >= "1.20.0":
            value = np.str_("test")
        else:
            value = np.str("test")
        self.assertTrue(value_not_empty(value))

        value = np.bool_(False)
        self.assertTrue(value_not_empty(value))

        value = np.bool_(True)
        self.assertTrue(value_not_empty(value))
