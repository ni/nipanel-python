"""Functions to convert between different data formats."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar

from google.protobuf import any_pb2, wrappers_pb2
from google.protobuf.message import Message

TPythonType = TypeVar("TPythonType", covariant=True)
TProtobufType = TypeVar("TProtobufType", bound=Message, covariant=True)

_logger = logging.getLogger(__name__)


class Converter(Generic[TPythonType, TProtobufType], ABC):
    """A class that defines how to convert between Python objects and protobuf Any messages."""

    @property
    @abstractmethod
    def python_type(self) -> Type[TPythonType]:
        """The Python type that this converter handles."""

    @property
    @abstractmethod
    def protobuf_message(self) -> Type[TProtobufType]:
        """The type-specific protobuf message for the Python type."""

    @property
    def protobuf_typename(self) -> str:
        """The protobuf name for the type."""
        return self.protobuf_message.DESCRIPTOR.full_name  # type: ignore[no-any-return]

    @abstractmethod
    def to_protobuf(self, python_value: Any) -> any_pb2.Any:
        """Convert the Python object to its type-specific protobuf message and pack it into an any_pb2.Any."""

    @abstractmethod
    def to_python(self, protobuf_value: any_pb2.Any) -> TPythonType:
        """Convert the protobuf message to its matching Python type."""


class BoolConverter(Converter[bool, wrappers_pb2.BoolValue]):
    """A converter for boolean types."""

    @property
    def python_type(self) -> Type[bool]:
        """The Python type that this converter handles."""
        return bool

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.BoolValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.BoolValue

    def to_protobuf(self, python_value: bool) -> any_pb2.Any:
        """Convert a bool to a protobuf Any."""
        wrapped_value = self.protobuf_message(value=python_value)
        as_any = any_pb2.Any()
        as_any.Pack(wrapped_value)
        return as_any

    def to_python(self, protobuf_value: any_pb2.Any) -> bool:
        """Convert the protobuf message to a Python bool."""
        protobuf_message = self.protobuf_message()
        did_unpack = protobuf_value.Unpack(protobuf_message)
        if not did_unpack:
            raise ValueError(f"Failed to unpack Any with type '{protobuf_value.TypeName()}'")
        return protobuf_message.value


class BytesConverter(Converter[bytes, wrappers_pb2.BytesValue]):
    """A converter for byte string types."""

    @property
    def python_type(self) -> Type[bytes]:
        """The Python type that this converter handles."""
        return bytes

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.BytesValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.BytesValue

    def to_protobuf(self, python_value: bytes) -> any_pb2.Any:
        """Convert bytes to a protobuf Any."""
        wrapped_value = self.protobuf_message(value=python_value)
        as_any = any_pb2.Any()
        as_any.Pack(wrapped_value)
        return as_any

    def to_python(self, protobuf_value: any_pb2.Any) -> bytes:
        """Convert the protobuf message to Python bytes."""
        protobuf_message = self.protobuf_message()
        did_unpack = protobuf_value.Unpack(protobuf_message)
        if not did_unpack:
            raise ValueError(f"Failed to unpack Any with type '{protobuf_value.TypeName()}'")
        return protobuf_message.value


class FloatConverter(Converter[float, wrappers_pb2.DoubleValue]):
    """A converter for floating point types."""

    @property
    def python_type(self) -> Type[float]:
        """The Python type that this converter handles."""
        return float

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.DoubleValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.DoubleValue

    def to_protobuf(self, python_value: float) -> any_pb2.Any:
        """Convert a float to a protobuf Any."""
        wrapped_value = self.protobuf_message(value=python_value)
        as_any = any_pb2.Any()
        as_any.Pack(wrapped_value)
        return as_any

    def to_python(self, protobuf_value: any_pb2.Any) -> float:
        """Convert the protobuf message to a Python float."""
        protobuf_message = self.protobuf_message()
        did_unpack = protobuf_value.Unpack(protobuf_message)
        if not did_unpack:
            raise ValueError(f"Failed to unpack Any with type '{protobuf_value.TypeName()}'")
        return protobuf_message.value


class IntConverter(Converter[int, wrappers_pb2.Int64Value]):
    """A converter for integer types."""

    @property
    def python_type(self) -> Type[int]:
        """The Python type that this converter handles."""
        return int

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.Int64Value]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.Int64Value

    def to_protobuf(self, python_value: int) -> any_pb2.Any:
        """Convert an int to a protobuf Any."""
        wrapped_value = self.protobuf_message(value=python_value)
        as_any = any_pb2.Any()
        as_any.Pack(wrapped_value)
        return as_any

    def to_python(self, protobuf_value: any_pb2.Any) -> int:
        """Convert the protobuf message to a Python int."""
        protobuf_message = self.protobuf_message()
        did_unpack = protobuf_value.Unpack(protobuf_message)
        if not did_unpack:
            raise ValueError(f"Failed to unpack Any with type '{protobuf_value.TypeName()}'")
        return protobuf_message.value


class StrConverter(Converter[str, wrappers_pb2.StringValue]):
    """A converter for text string types."""

    @property
    def python_type(self) -> Type[str]:
        """The Python type that this converter handles."""
        return str

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.StringValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.StringValue

    def to_protobuf(self, python_value: str) -> any_pb2.Any:
        """Convert a str to a protobuf Any."""
        wrapped_value = self.protobuf_message(value=python_value)
        as_any = any_pb2.Any()
        as_any.Pack(wrapped_value)
        return as_any

    def to_python(self, protobuf_value: any_pb2.Any) -> str:
        """Convert the protobuf message to a Python string."""
        protobuf_message = self.protobuf_message()
        did_unpack = protobuf_value.Unpack(protobuf_message)
        if not did_unpack:
            raise ValueError(f"Failed to unpack Any with type '{protobuf_value.TypeName()}'")
        return protobuf_message.value


# FFV -- consider adding a RegisterConverter mechanism
_CONVERTIBLE_TYPES = [
    BoolConverter(),
    BytesConverter(),
    FloatConverter(),
    IntConverter(),
    StrConverter(),
]

_CONVERTER_FOR_PYTHON_TYPE = {entry.python_type: entry for entry in _CONVERTIBLE_TYPES}
_CONVERTER_FOR_GRPC_TYPE = {entry.protobuf_typename: entry for entry in _CONVERTIBLE_TYPES}
_SUPPORTED_PYTHON_TYPES = _CONVERTER_FOR_PYTHON_TYPE.keys()


def to_any(python_value: Any) -> any_pb2.Any:
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

    converter = _CONVERTER_FOR_PYTHON_TYPE[best_matching_type]
    return converter.to_protobuf(python_value)


def from_any(protobuf_any: any_pb2.Any) -> Any:
    """Convert a protobuf Any to a Python object."""
    if not isinstance(protobuf_any, any_pb2.Any):
        raise ValueError(f"Unexpected type: {type(protobuf_any)}")

    underlying_typename = protobuf_any.TypeName()
    _logger.debug(f"Unpacking type '{underlying_typename}'")

    converter = _CONVERTER_FOR_GRPC_TYPE[underlying_typename]
    return converter.to_python(protobuf_any)
