import unittest

import numpy as np

from askanna.core.utils import json_serializer, translate_dtype


class NumPyConverterTest(unittest.TestCase):
    def test_serialize_nd_float(self):
        self.assertEqual(json_serializer(np.float64(5.21)), 5.21)
        self.assertEqual(json_serializer(np.array([1, 5, 9])), [1, 5, 9])

    def test_translation(self):
        self.assertEqual(translate_dtype(np.bool_(True)), "boolean")
        self.assertEqual(translate_dtype(np.int64(5)), "integer")
        self.assertEqual(translate_dtype(np.float64(5.21)), "float")
        self.assertEqual(translate_dtype(np.half(5.21)), "float")
