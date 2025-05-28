"""Functions to convert between different data formats."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, List, Tuple, Type, TypeVar

from google.protobuf import any_pb2, wrappers_pb2
from google.protobuf.message import Message
from ni.pythonpanel.v1 import python_panel_types_pb2

_TPythonContainerType = TypeVar("_TPythonContainerType")
_TPythonType = TypeVar("_TPythonType")
_TProtobufType = TypeVar("_TProtobufType", bound=Message)

_logger = logging.getLogger(__name__)


class Converter(Generic[_TPythonContainerType, _TPythonType, _TProtobufType], ABC):
    """A class that defines how to convert between Python objects and protobuf Any messages."""

    @property
    @abstractmethod
    def python_type(self) -> Tuple[_TPythonContainerType, Type[_TPythonType]]:
        """The Python type that this converter handles."""

    @property
    @abstractmethod
    def protobuf_message(self) -> Type[_TProtobufType]:
        """The type-specific protobuf message for the Python type."""

    @property
    def protobuf_typename(self) -> str:
        """The protobuf name for the type."""
        return self.protobuf_message.DESCRIPTOR.full_name  # type: ignore[no-any-return]

    def to_protobuf_any(self, python_container: Type[_TPythonContainerType], python_value: _TPythonType) -> any_pb2.Any:
        """Convert the Python object to its type-specific message and pack it as any_pb2.Any."""
        message = self.to_protobuf_message(python_container, python_value)
        as_any = any_pb2.Any()
        as_any.Pack(message)
        return as_any

    @abstractmethod
    def to_protobuf_message(self, python_container: Type[_TPythonContainerType], python_value: _TPythonType) -> _TProtobufType:
        """Convert the Python object to its type-specific message."""

    def to_python(self, protobuf_value: any_pb2.Any) -> _TPythonType:
        """Convert the protobuf Any message to its matching Python type."""
        protobuf_message = self.protobuf_message()
        did_unpack = protobuf_value.Unpack(protobuf_message)
        if not did_unpack:
            raise ValueError(f"Failed to unpack Any with type '{protobuf_value.TypeName()}'")
        return self.to_python_value(protobuf_message)

    @abstractmethod
    def to_python_value(self, protobuf_message: _TProtobufType) -> _TPythonType:
        """Convert the protobuf wrapper message to its matching Python type."""


class BoolConverter(Converter[None, bool, wrappers_pb2.BoolValue]):
    """A converter for boolean types."""

    @property
    def python_type(self) -> Tuple[None, Type[bool]]:
        """The Python type that this converter handles."""
        return (None, bool)

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.BoolValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.BoolValue

    def to_protobuf_message(self, python_container: Type[None], python_value: bool) -> wrappers_pb2.BoolValue:
        """Convert the Python bool to a protobuf wrappers_pb2.BoolValue."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_value: wrappers_pb2.BoolValue) -> bool:
        """Convert the protobuf message to a Python bool."""
        return protobuf_value.value


class BytesConverter(Converter[None, bytes, wrappers_pb2.BytesValue]):
    """A converter for byte string types."""

    @property
    def python_type(self) -> Tuple[None, Type[bytes]]:
        """The Python type that this converter handles."""
        return (None, bytes)

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.BytesValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.BytesValue

    def to_protobuf_message(self, python_container: Type[None], python_value: bytes) -> wrappers_pb2.BytesValue:
        """Convert the Python bytes string to a protobuf wrappers_pb2.BytesValue."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_value: wrappers_pb2.BytesValue) -> bytes:
        """Convert the protobuf message to a Python bytes string."""
        return protobuf_value.value


class FloatConverter(Converter[None, float, wrappers_pb2.DoubleValue]):
    """A converter for floating point types."""

    @property
    def python_type(self) -> Tuple[None, Type[float]]:
        """The Python type that this converter handles."""
        return (None, float)

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.DoubleValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.DoubleValue

    def to_protobuf_message(self, python_container: Type[None], python_value: float) -> wrappers_pb2.DoubleValue:
        """Convert the Python float to a protobuf wrappers_pb2.DoubleValue."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_value: wrappers_pb2.DoubleValue) -> float:
        """Convert the protobuf message to a Python float."""
        return protobuf_value.value


class IntConverter(Converter[None, int, wrappers_pb2.Int64Value]):
    """A converter for integer types."""

    @property
    def python_type(self) -> Tuple[None, Type[int]]:
        """The Python type that this converter handles."""
        return (None, int)

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.Int64Value]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.Int64Value

    def to_protobuf_message(self, python_container: Type[None], python_value: int) -> wrappers_pb2.Int64Value:
        """Convert the Python int to a protobuf wrappers_pb2.Int64Value."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_value: wrappers_pb2.Int64Value) -> int:
        """Convert the protobuf message to a Python int."""
        return protobuf_value.value


class StrConverter(Converter[None, str, wrappers_pb2.StringValue]):
    """A converter for text string types."""

    @property
    def python_type(self) -> Tuple[None, Type[str]]:
        """The Python type that this converter handles."""
        return (None, str)

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.StringValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.StringValue

    def to_protobuf_message(self, python_container: Type[None], python_value: str) -> wrappers_pb2.StringValue:
        """Convert the Python str to a protobuf wrappers_pb2.StringValue."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_value: wrappers_pb2.StringValue) -> str:
        """Convert the protobuf message to a Python string."""
        return protobuf_value.value


class IntListConverter(Converter[List[int], int, python_panel_types_pb2.IntSequence]):
    """A converter for sequences of integer types."""

    @property
    ##def python_type(self) -> Type[List[int]]:  # [<class 'bool'>, <class 'bytes'>, <class 'float'>, <class 'int'>, <class 'str'>, list[int]]
    def python_type(self) -> Tuple[list, Type[int]]:
        """The Python type that this converter handles."""
        return (list, int)

    @property
    def protobuf_message(self) -> Type[python_panel_types_pb2.IntSequence]:
        """The type-specific protobuf message for the Python type."""
        return python_panel_types_pb2.IntSequence

    def to_protobuf_message(self, python_container: Type[List[int]], python_value: List[int]) -> python_panel_types_pb2.IntSequence:
        """Convert the Python list[int] to a protobuf python_panel_types_pb2.IntSequence."""
        message = self.protobuf_message(values=python_value)
        return message

    def to_python_value(self, protobuf_message: python_panel_types_pb2.IntSequence) -> List[int]:
        return list(protobuf_message.values)


_CONVERTIBLE_SCALAR_TYPES = {
    bool,
    bytes,
    float,
    int,
    str,
}

_CONVERTIBLE_CONTAINER_TYPES = {
    list,
    set,
    frozenset,
    tuple,
}

# FFV -- consider adding a RegisterConverter mechanism
_CONVERTIBLE_TYPES: list[Converter[Any, Any, Any]] = [
    BoolConverter(),
    BytesConverter(),
    FloatConverter(),
    IntConverter(),
    StrConverter(),
    IntListConverter(),
]

_CONVERTER_FOR_PYTHON_TYPE = {entry.python_type: entry for entry in _CONVERTIBLE_TYPES}
_CONVERTER_FOR_GRPC_TYPE = {entry.protobuf_typename: entry for entry in _CONVERTIBLE_TYPES}
_SUPPORTED_PYTHON_TYPES = _CONVERTER_FOR_PYTHON_TYPE.keys()


def to_any(python_value: object) -> any_pb2.Any:
    """Convert a Python object to a protobuf Any."""
    underlying_parents = type(python_value).mro()  # This covers enum.IntEnum and similar

    # Check for container
    value_is_container = _CONVERTIBLE_CONTAINER_TYPES.intersection(underlying_parents)
    if value_is_container:
        # Assume sized -- generators not supported, callers must use list(), set(), ... as desired
        if len(python_value) == 0:
            underlying_parents = type(None).mro()
        else:
            # Assume homogenous -- sequences of mixed-types not supported
            visitor = iter(python_value)
            first_value = next(visitor)
            underlying_parents = type(first_value).mro()
        container_type = value_is_container.pop()
    else:
        container_type = None
    payload_type = underlying_parents[0]

    # Check the payload type
    best_matching_type = next(
        ((container_type, parent) for parent in underlying_parents if (container_type, parent) in _SUPPORTED_PYTHON_TYPES), None
    )
    if not best_matching_type:
        raise TypeError(
            f"Unsupported type: ({container_type}, {payload_type}) with parents {underlying_parents}. Supported types are: {_SUPPORTED_PYTHON_TYPES}"
        )
    _logger.debug(f"Best matching type for '{repr(python_value)}' resolved to {best_matching_type}")

    converter = _CONVERTER_FOR_PYTHON_TYPE[best_matching_type]
    return converter.to_protobuf_any(container_type, python_value)


def from_any(protobuf_any: any_pb2.Any) -> object:
    """Convert a protobuf Any to a Python object."""
    if not isinstance(protobuf_any, any_pb2.Any):
        raise ValueError(f"Unexpected type: {type(protobuf_any)}")

    underlying_typename = protobuf_any.TypeName()
    _logger.debug(f"Unpacking type '{underlying_typename}'")

    converter = _CONVERTER_FOR_GRPC_TYPE[underlying_typename]
    return converter.to_python(protobuf_any)
