"""Classes to convert between measurement specific protobuf types and containers."""

from typing import Type, Union

from ni.protobuf.types import scalar_pb2
from nitypes.scalar import Scalar
from typing_extensions import TypeAlias

from nipanel.converters import Converter

_AnyScalarType: TypeAlias = Union[bool, int, float, str]
SCALAR_TYPE_TO_PB_ATTR_MAP = {
    bool: "bool_value",
    int: "int32_value",
    float: "double_value",
    str: "string_value",
}


class ScalarConverter(Converter[Scalar[_AnyScalarType], scalar_pb2.ScalarData]):
    """A converter for Scalar objects."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return Scalar.__name__

    @property
    def protobuf_message(self) -> Type[scalar_pb2.ScalarData]:
        """The type-specific protobuf message for the Python type."""
        return scalar_pb2.ScalarData

    def to_protobuf_message(self, python_value: Scalar[_AnyScalarType]) -> scalar_pb2.ScalarData:
        """Convert the Python Scalar to a protobuf scalar_pb2.ScalarData."""
        message = self.protobuf_message()
        message.units = python_value.units

        value_attr = SCALAR_TYPE_TO_PB_ATTR_MAP.get(type(python_value.value), None)
        if not value_attr:
            raise TypeError(f"Unexpected type for python_value.value: {type(python_value.value)}")
        setattr(message, value_attr, python_value.value)

        return message

    def to_python_value(self, protobuf_value: scalar_pb2.ScalarData) -> Scalar[_AnyScalarType]:
        """Convert the protobuf message to a Python Scalar."""
        if protobuf_value.units is None:
            raise ValueError("protobuf.units cannot be None.")

        pb_type = str(protobuf_value.WhichOneof("value"))
        if pb_type not in SCALAR_TYPE_TO_PB_ATTR_MAP.values():
            raise ValueError(f"Unexpected value for protobuf_value.WhichOneOf: {pb_type}")

        value = getattr(protobuf_value, pb_type)
        return Scalar(value, protobuf_value.units)
