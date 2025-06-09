"""Classes to convert between measurement specific protobuf types and containers."""

from typing import Any, Type

from ni.protobuf.types import scalar_pb2
from nitypes.scalar import Scalar

from nipanel.converters import Converter


class ScalarConverter(Converter[Scalar[Any], scalar_pb2.ScalarData]):
    """A converter for Scalar objects."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return Scalar.__name__

    @property
    def protobuf_message(self) -> Type[scalar_pb2.ScalarData]:
        """The type-specific protobuf message for the Python type."""
        return scalar_pb2.ScalarData

    def to_protobuf_message(self, python_value: Scalar[Any]) -> scalar_pb2.ScalarData:
        """Convert the Python Scalar to a protobuf scalar_pb2.ScalarData."""
        message = self.protobuf_message()
        message.units = python_value.units
        if isinstance(python_value.value, bool):
            message.bool_value = python_value.value
        elif isinstance(python_value.value, int):
            message.int32_value = python_value.value
        elif isinstance(python_value.value, float):
            message.double_value = python_value.value
        elif isinstance(python_value.value, str):
            message.string_value = python_value.value
        else:
            raise TypeError(f"Unexpected type for python_value.value: {type(python_value.value)}")

        return message

    def to_python_value(self, protobuf_value: scalar_pb2.ScalarData) -> Scalar[Any]:
        """Convert the protobuf message to a Python Scalar."""
        if protobuf_value.units is None:
            raise ValueError("protobuf.units cannot be None.")

        pb_type = protobuf_value.WhichOneof("value")
        if pb_type == "bool_value":
            return Scalar(protobuf_value.bool_value, protobuf_value.units)
        elif pb_type == "int32_value":
            return Scalar(protobuf_value.int32_value, protobuf_value.units)
        elif pb_type == "double_value":
            return Scalar(protobuf_value.double_value, protobuf_value.units)
        elif pb_type == "string_value":
            return Scalar(protobuf_value.string_value, protobuf_value.units)
        else:
            raise ValueError(f"Unexpected value for protobuf_value.WhichOneOf: {pb_type}")
