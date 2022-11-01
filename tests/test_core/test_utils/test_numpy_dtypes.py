import unittest

import numpy as np

from askanna.core.utils.object import get_type, json_serializer


class NumPyConverterTest(unittest.TestCase):
    def test_serialize_nd_float(self):
        self.assertEqual(json_serializer(np.float64(5.21)), 5.21)
        self.assertEqual(json_serializer(np.array([1, 5, 9])), [1, 5, 9])

    def test_translation(self):
        self.assertEqual(get_type(np.bool_(True)), "boolean")
        self.assertEqual(get_type(np.int64(5)), "integer")
        self.assertEqual(get_type(np.float64(5.21)), "float")
        self.assertEqual(get_type(np.half(5.21)), "float")
