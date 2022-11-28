import datetime
from typing import Any, Tuple

supported_data_types = {
    # primitive types
    "bool": "boolean",
    "int": "integer",
    "float": "float",
    "str": "string",
    # complex types
    "datetime.datetime": "datetime",
    "datetime.time": "time",
    "datetime.date": "date",
    "dict": "dictionary",
    "list": "list",
    "tag": "tag",
}

# If numpy as installed, we add the numpy types to the supported types
try:
    import numpy as np  # noqa: F401
except ImportError:
    NUMPY_INSTALLED = False
else:
    NUMPY_INSTALLED = True
    supported_data_types.update(
        {
            # Source Numpy documentation, a.o. https://numpy.org/doc/stable/user/basics.types.html
            "numpy.bool_": "boolean",
            "numpy.intc": "integer",
            "numpy.int": "integer",
            "numpy.int_": "integer",
            "numpy.uint": "integer",
            "numpy.short": "integer",
            "numpy.ushort": "integer",
            "numpy.longlong": "integer",
            "numpy.ulonglong": "integer",
            "numpy.half": "float",
            "numpy.float16": "float",
            "numpy.single": "float",
            "numpy.double": "float",
            "numpy.longdouble": "float",
            "numpy.csingle": "float",
            "numpy.cdouble": "float",
            "numpy.clongdouble": "float",
            "numpy.str": "string",
            "numpy.str_": "string",
            # List type
            "numpy.array": "list",
            "numpy.ndarray": "list",
            # C-derived names and more "complex" types
            # Source: https://numpy.org/doc/stable/reference/arrays.scalars.html#sized-aliases
            "numpy.bool8": "boolean",
            "numpy.int8": "integer",
            "numpy.int16": "integer",
            "numpy.int32": "integer",
            "numpy.int64": "integer",
            "numpy.uint8": "integer",
            "numpy.uint16": "integer",
            "numpy.uint32": "integer",
            "numpy.uint64": "integer",
            "numpy.intp": "integer",
            "numpy.uintp": "integer",
            "numpy.float32": "float",
            "numpy.float64": "float",
            "numpy.float_": "float",
            "numpy.complex64": "float",
            "numpy.complex128": "float",
            "numpy.complex192": "float",
            "numpy.complex256": "float",
            "numpy.complex_": "float",
            "numpy.longfloat": "float",
            "numpy.singlecomplex": "float",
            "numpy.cfloat": "float",
            "numpy.longcomplex": "float",
            "numpy.clongfloat": "float",
            "numpy.unicode_": "string",
        }
    )


def object_fullname(o):
    # https://stackoverflow.com/a/2020083
    # o.__module__ + "." + o.__class__.__qualname__ is an example in
    # this context of H.L. Mencken's "neat, plausible, and wrong."
    # Python makes no guarantees as to whether the __module__ special
    # attribute is defined, so we take a more circumspect approach.
    # Alas, the module name is explicitly excluded from __qualname__
    # in Python 3.

    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return o.__class__.__name__  # Avoid reporting __builtin__
    else:
        return module + "." + o.__class__.__name__


def get_type(value: Any) -> str:
    """
    Return the full name of the type, if not listed, return the typename from the input
    """
    typename = object_fullname(value)
    dtype = supported_data_types.get(typename, typename)

    if typename in ("numpy.array", "numpy.ndarray"):
        dtype_list = supported_data_types.get("numpy." + value.dtype.name)
        if dtype_list:
            dtype = "list_" + dtype_list
    elif typename == "list":
        dtype_list = None
        for val in value:
            if type(val) == bool and dtype_list in (None, "boolean"):
                dtype_list = "boolean"
            elif type(val) == int and dtype_list in (None, "integer"):
                dtype_list = "integer"
            elif type(val) in (int, float) and dtype_list in (None, "integer", "float"):
                dtype_list = "float"
            elif type(val) == str and dtype_list in (None, "string"):
                dtype_list = "string"
            elif type(val) == datetime.datetime and dtype_list in (None, "datetime"):
                dtype_list = "datetime"
            elif type(val) == datetime.time and dtype_list in (None, "time"):
                dtype_list = "time"
            elif type(val) == datetime.date and dtype_list in (None, "date"):
                dtype_list = "date"
            else:
                dtype_list = "mixed"
                break

        if dtype_list and dtype_list != "mixed":
            dtype = "list_" + dtype_list

    return dtype


def validate_value(value: Any) -> bool:
    """
    Validate whether the value set is supported
    """

    return object_fullname(value) in supported_data_types


def transform_value(value: Any) -> Tuple[Any, bool]:
    """
    Transform values in support datatypes
    """
    if object_fullname(value) == "range":
        return list(value), True

    return value, False


def prepare_and_validate_value(value: Any) -> Tuple[Any, bool]:
    """
    Validate value and if necessary transform values in support datatypes
    """
    if validate_value(value):
        return value, True

    # Try to transform the value
    value, transform = transform_value(value)
    if transform:
        return value, True

    return value, False


def value_not_empty(value: Any) -> bool:
    """
    Check if the value is not empty
    """
    if value.__class__.__module__ == "numpy":
        try:
            if value.any() or isinstance(value, np.bool_):
                return True
        except np.core._exceptions.UFuncTypeError:  # type: ignore
            pass
    if value or isinstance(value, bool):
        return True
    return False


def serialize_numpy_for_json(obj):
    # the o.item() is a generic method on each numpy dtype.
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def json_serializer(obj):
    if isinstance(obj, (datetime.time, datetime.date, datetime.datetime)):
        return obj.isoformat()
    if NUMPY_INSTALLED:
        return serialize_numpy_for_json(obj)
    return obj
