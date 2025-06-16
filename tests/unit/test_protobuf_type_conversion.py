import pytest
from ni.protobuf.types.scalar_pb2 import ScalarData
from nitypes.scalar import Scalar

from nipanel.converters.protobuf_types import ScalarConverter


# ========================================================
# Protobuf to Python
# ========================================================
def test___bool_scalar_protobuf___convert___valid_bool_scalar() -> None:
    protobuf_value = ScalarData()
    protobuf_value.units = "volts"
    protobuf_value.bool_value = True

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, bool)
    assert python_value.value is True
    assert python_value.units == "volts"


def test___int32_scalar_protobuf___convert___valid_int_scalar() -> None:
    protobuf_value = ScalarData()
    protobuf_value.units = "volts"
    protobuf_value.int32_value = 10

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, int)
    assert python_value.value == 10
    assert python_value.units == "volts"


def test___double_scalar_protobuf___convert___valid_float_scalar() -> None:
    protobuf_value = ScalarData()
    protobuf_value.units = "volts"
    protobuf_value.double_value = 20.0

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, float)
    assert python_value.value == 20.0
    assert python_value.units == "volts"


def test___string_scalar_protobuf___convert___valid_str_scalar() -> None:
    protobuf_value = ScalarData()
    protobuf_value.units = "volts"
    protobuf_value.string_value = "value"

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, str)
    assert python_value.value == "value"
    assert python_value.units == "volts"


def test___scalar_protobuf_value_unset___convert___throws_type_error() -> None:
    protobuf_value = ScalarData()
    protobuf_value.units = "volts"

    converter = ScalarConverter()
    with pytest.raises(ValueError) as exc:
        _ = converter.to_python_value(protobuf_value)

    assert exc.value.args[0].startswith("Unexpected value for protobuf_value.WhichOneOf")


def test___scalar_protobuf_units_unset___convert___python_units_blank() -> None:
    protobuf_value = ScalarData()
    protobuf_value.bool_value = True

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, bool)
    assert python_value.value is True
    assert python_value.units == ""


# ========================================================
# Python to Protobuf
# ========================================================
def test___bool_scalar___convert___valid_bool_scalar_protobuf() -> None:
    python_value = Scalar(True, "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "bool_value"
    assert protobuf_value.bool_value is True
    assert protobuf_value.units == "volts"


def test___int_scalar___convert___valid_int32_scalar_protobuf() -> None:
    python_value = Scalar(10, "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "int32_value"
    assert protobuf_value.int32_value == 10
    assert protobuf_value.units == "volts"


def test___float_scalar___convert___valid_double_scalar_protobuf() -> None:
    python_value = Scalar(20.0, "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "double_value"
    assert protobuf_value.double_value == 20.0
    assert protobuf_value.units == "volts"


def test___str_scalar___convert___valid_string_scalar_protobuf() -> None:
    python_value = Scalar("value", "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "string_value"
    assert protobuf_value.string_value == "value"
    assert protobuf_value.units == "volts"


def test___scalar_units_unset___convert___protobuf_units_blank() -> None:
    python_value = Scalar(10)

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "int32_value"
    assert protobuf_value.int32_value == 10
    assert protobuf_value.units == ""
