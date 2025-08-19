import pytest
from ni.protobuf.types import array_pb2, attribute_value_pb2, scalar_pb2, vector_pb2
from nitypes.scalar import Scalar
from nitypes.vector import Vector
from typing_extensions import Mapping

from nipanel.converters.protobuf_types import (
    Double2DArrayConverter,
    ScalarConverter,
    VectorConverter,
)


# ========================================================
# list[list[float]] to Double2DArray
# Other collection types are tested in test_convert.py
# ========================================================
@pytest.mark.parametrize(
    "list_of_lists, expected_data, expected_rows, expected_columns",
    [
        ([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], [1.0, 2.0, 3.0, 4.0, 5.0, 6.0], 3, 2),
        ([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], [1.0, 2.0, 3.0, 4.0, 5.0, 6.0], 2, 3),
    ],
)
def test___list_of_lists___convert___valid_double2darray(
    list_of_lists: list[list[float]],
    expected_data: list[float],
    expected_rows: int,
    expected_columns: int,
) -> None:
    converter = Double2DArrayConverter()
    result = converter.to_protobuf_message(list_of_lists)

    assert result.data == expected_data
    assert result.rows == expected_rows
    assert result.columns == expected_columns


def test___list_of_lists_inconsistent_column_length___convert___throws_value_error() -> None:
    converter = Double2DArrayConverter()

    with pytest.raises(ValueError):
        _ = converter.to_protobuf_message([[1.0, 2.0], [3.0, 4.0, 5.0]])


# ========================================================
# Double2DArray to list[list[float]]
# Other collection types are tested in test_convert.py
# ========================================================
@pytest.mark.parametrize(
    "double2darray, expected_data",
    [
        (
            array_pb2.Double2DArray(rows=3, columns=2, data=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]),
            [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
        ),
        (
            array_pb2.Double2DArray(rows=2, columns=3, data=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]),
            [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
        ),
    ],
)
def test___double2darray___convert___valid_list_of_lists(
    double2darray: array_pb2.Double2DArray, expected_data: list[list[float]]
) -> None:
    converter = Double2DArrayConverter()
    list_of_lists = converter.to_python_value(double2darray)

    assert list_of_lists == expected_data


def test___double2darray_invalid_num_columns___convert___throws_value_error() -> None:
    double2darray = array_pb2.Double2DArray(rows=1, columns=2, data=[1.0, 2.0, 3.0])
    converter = Double2DArrayConverter()

    with pytest.raises(ValueError):
        _ = converter.to_python_value(double2darray)


def test___double2darray_empty_data___convert___returns_empty_list() -> None:
    double2darray = array_pb2.Double2DArray(rows=0, columns=0, data=[])
    converter = Double2DArrayConverter()

    list_of_lists = converter.to_python_value(double2darray)

    assert not list_of_lists


# ========================================================
# Scalar: Protobuf to Python
# ========================================================
def test___string_scalar_protobuf___convert___valid_str_scalar() -> None:
    attrs = _units_to_attribute_map("volts")
    protobuf_value = scalar_pb2.Scalar(attributes=attrs)
    protobuf_value.string_value = "value"

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, str)
    assert python_value.value == "value"
    assert python_value.units == "volts"


# ========================================================
# Scalar: Python to Protobuf
# ========================================================
def test___str_scalar___convert___valid_string_scalar_protobuf() -> None:
    python_value = Scalar("value", "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "string_value"
    assert protobuf_value.string_value == "value"
    assert protobuf_value.attributes["NI_UnitDescription"].string_value == "volts"


# ========================================================
# Vector: Protobuf to Python
# ========================================================
def test___string_vector_protobuf___convert___valid_str_vector() -> None:
    attrs = _units_to_attribute_map("volts")
    protobuf_value = vector_pb2.Vector(
        attributes=attrs,
        string_array=array_pb2.StringArray(values=["one", "two", "three"]),
    )

    converter = VectorConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value, Vector)
    assert list(python_value) == ["one", "two", "three"]
    assert python_value.units == "volts"


# ========================================================
# Vector: Python to Protobuf
# ========================================================
def test___str_vector___convert___valid_string_vector_protobuf() -> None:
    python_value = Vector(["one", "two", "three"], "volts")

    converter = VectorConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert isinstance(protobuf_value, vector_pb2.Vector)
    assert protobuf_value.WhichOneof("value") == "string_array"
    assert list(protobuf_value.string_array.values) == ["one", "two", "three"]
    assert protobuf_value.attributes["NI_UnitDescription"].string_value == "volts"


def _units_to_attribute_map(units: str) -> Mapping[str, attribute_value_pb2.AttributeValue]:
    value = attribute_value_pb2.AttributeValue(string_value=units)
    return {"NI_UnitDescription": value}
