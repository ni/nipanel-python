"""Functions to convert between different data formats."""

from __future__ import annotations

import logging
from typing import Protocol

from google.protobuf import any_pb2, wrappers_pb2
from google.protobuf.message import Message

_logger = logging.getLogger(__name__)


class Converter(Protocol):
    """A class that defines how to convert between Python and protobuf types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""

    @property
    def protobuf_message(self) -> type:
        """The protobuf message for the type."""

    def to_protobuf(self, value: object) -> Message:
        """Convert a Python object to a protobuf message."""

    @property
    def protobuf_typename(self) -> str:
        """The protobuf name for the type."""
        return self.protobuf_message.DESCRIPTOR.full_name


class BoolConverter(Converter):
    """A converter for bool types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return bool

    @property
    def protobuf_message(self) -> type:
        """The protobuf message for the type."""
        return wrappers_pb2.BoolValue

    def to_protobuf(self, value: object) -> wrappers_pb2.BoolValue:
        """Convert a bool to a protobuf BoolValue."""
        assert isinstance(value, bool), f"Expected bool, got {type(value)}"
        return self.protobuf_message(value=value)


class BytesConverter(Converter):
    """A converter for bytes types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return bytes

    @property
    def protobuf_message(self) -> type:
        """The protobuf message for the type."""
        return wrappers_pb2.BytesValue

    def to_protobuf(self, value: object) -> wrappers_pb2.BytesValue:
        """Convert bytes to a protobuf BytesValue."""
        assert isinstance(value, bytes), f"Expected bytes, got {type(value)}"
        return self.protobuf_message(value=value)


class FloatConverter(Converter):
    """A converter for float types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return float

    @property
    def protobuf_message(self) -> type:
        """The protobuf message for the type."""
        return wrappers_pb2.DoubleValue

    def to_protobuf(self, value: object) -> wrappers_pb2.DoubleValue:
        """Convert a float to a protobuf DoubleValue."""
        assert isinstance(value, float), f"Expected float, got {type(value)}"
        return self.protobuf_message(value=value)


class IntConverter(Converter):
    """A converter for int types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return int

    @property
    def protobuf_message(self) -> type:
        """The protobuf message for the type."""
        return wrappers_pb2.Int64Value

    def to_protobuf(self, value: object) -> wrappers_pb2.Int64Value:
        """Convert an int to a protobuf Int64Value."""
        assert isinstance(value, int), f"Expected int, got {type(value)}"
        return self.protobuf_message(value=value)


class StrConverter(Converter):
    """A converter for str types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return str

    @property
    def protobuf_message(self) -> type:
        """The protobuf message for the type."""
        return wrappers_pb2.StringValue

    def to_protobuf(self, value: object) -> wrappers_pb2.StringValue:
        """Convert a str to a protobuf StringValue."""
        assert isinstance(value, str), f"Expected str, got {type(value)}"
        return self.protobuf_message(value=value)


_CONVERTIBLE_TYPES = [
    BoolConverter(),
    BytesConverter(),
    FloatConverter(),
    IntConverter(),
    StrConverter(),
]

_CONVERTER_FOR_PYTHON_TYPE = {
    entry.python_type: entry for entry in _CONVERTIBLE_TYPES
}

_CONVERTER_FOR_GRPC_TYPE = {
    entry.protobuf_typename: entry for entry in _CONVERTIBLE_TYPES
}

_SUPPORTED_PYTHON_TYPES = _CONVERTER_FOR_PYTHON_TYPE.keys()


def to_any(python_value: object) -> any_pb2.Any:
    """Convert a Python object to a protobuf Any."""
    underlying_parents = type(python_value).mro()  # This covers enum.IntEnum and similar

    best_matching_type = next(
        (parent for parent in underlying_parents if parent in _SUPPORTED_PYTHON_TYPES), None
    )
    if not best_matching_type:
        raise TypeError(
            f"Unsupported type: {type(python_value)} with parents {underlying_parents}. Supported types are: {_SUPPORTED_PYTHON_TYPES}"
        )
    _logger.debug(f"Best matching type for '{repr(python_value)}' resolved to {best_matching_type}")

    the_any = any_pb2.Any()
    converter = _CONVERTER_FOR_PYTHON_TYPE[best_matching_type]
    wrapped_value = converter.to_protobuf(python_value)
    the_any.Pack(wrapped_value)
    return the_any


def from_any(protobuf_any: any_pb2.Any) -> object:
    """Convert a protobuf Any to a Python object."""
    if not isinstance(protobuf_any, any_pb2.Any):
        raise ValueError(f"Unexpected type: {type(protobuf_any)}")

    underlying_typename = protobuf_any.TypeName()
    _logger.debug(f"Unpacking type '{underlying_typename}'")

    converter = _CONVERTER_FOR_GRPC_TYPE[underlying_typename]
    protobuf_message = converter.protobuf_message()
    did_unpack = protobuf_any.Unpack(protobuf_message)
    if not did_unpack:
        raise ValueError(f"Failed to unpack Any with underlying type '{underlying_typename}'")

    return protobuf_message.value
