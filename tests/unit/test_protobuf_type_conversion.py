import pytest
from ni.protobuf.types import array_pb2, attribute_value_pb2, scalar_pb2
from nitypes.scalar import Scalar
from typing_extensions import Mapping

from nipanel.converters.protobuf_types import Double2DArrayConverter, ScalarConverter


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
def test___bool_scalar_protobuf___convert___valid_bool_scalar() -> None:
    attrs = _units_to_scalar_attribute_map("volts")
    protobuf_value = scalar_pb2.Scalar(attributes=attrs)
    protobuf_value.bool_value = True

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, bool)
    assert python_value.value is True
    assert python_value.units == "volts"


def test___int32_scalar_protobuf___convert___valid_int_scalar() -> None:
    attrs = _units_to_scalar_attribute_map("volts")
    protobuf_value = scalar_pb2.Scalar(attributes=attrs)
    protobuf_value.sint32_value = 10

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, int)
    assert python_value.value == 10
    assert python_value.units == "volts"


def test___double_scalar_protobuf___convert___valid_float_scalar() -> None:
    attrs = _units_to_scalar_attribute_map("volts")
    protobuf_value = scalar_pb2.Scalar(attributes=attrs)
    protobuf_value.double_value = 20.0

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, float)
    assert python_value.value == 20.0
    assert python_value.units == "volts"


def test___string_scalar_protobuf___convert___valid_str_scalar() -> None:
    attrs = _units_to_scalar_attribute_map("volts")
    protobuf_value = scalar_pb2.Scalar(attributes=attrs)
    protobuf_value.string_value = "value"

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, str)
    assert python_value.value == "value"
    assert python_value.units == "volts"


def test___scalar_protobuf_value_unset___convert___throws_type_error() -> None:
    attrs = _units_to_scalar_attribute_map("volts")
    protobuf_value = scalar_pb2.Scalar(attributes=attrs)

    converter = ScalarConverter()
    with pytest.raises(ValueError) as exc:
        _ = converter.to_python_value(protobuf_value)

    assert exc.value.args[0].startswith("Could not determine the data type of 'value'.")


def test___scalar_protobuf_units_unset___convert___python_units_blank() -> None:
    protobuf_value = scalar_pb2.Scalar()
    protobuf_value.bool_value = True

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, bool)
    assert python_value.value is True
    assert python_value.units == ""


# ========================================================
# Scalar: Python to Protobuf
# ========================================================
def test___bool_scalar___convert___valid_bool_scalar_protobuf() -> None:
    python_value = Scalar(True, "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "bool_value"
    assert protobuf_value.bool_value is True
    assert protobuf_value.attributes["NI_UnitDescription"].string_value == "volts"


def test___int_scalar___convert___valid_int32_scalar_protobuf() -> None:
    python_value = Scalar(10, "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "sint32_value"
    assert protobuf_value.sint32_value == 10
    assert protobuf_value.attributes["NI_UnitDescription"].string_value == "volts"


def test___float_scalar___convert___valid_double_scalar_protobuf() -> None:
    python_value = Scalar(20.0, "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "double_value"
    assert protobuf_value.double_value == 20.0
    assert protobuf_value.attributes["NI_UnitDescription"].string_value == "volts"


def test___str_scalar___convert___valid_string_scalar_protobuf() -> None:
    python_value = Scalar("value", "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "string_value"
    assert protobuf_value.string_value == "value"
    assert protobuf_value.attributes["NI_UnitDescription"].string_value == "volts"


def test___scalar_units_unset___convert___protobuf_units_blank() -> None:
    python_value = Scalar(10)

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "sint32_value"
    assert protobuf_value.sint32_value == 10
    assert protobuf_value.attributes["NI_UnitDescription"].string_value == ""


def _units_to_scalar_attribute_map(units: str) -> Mapping[str, attribute_value_pb2.AttributeValue]:
    value = attribute_value_pb2.AttributeValue(string_value=units)
    return {"NI_UnitDescription": value}
