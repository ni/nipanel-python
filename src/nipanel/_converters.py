"""Functions to convert between different data formats."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Collection
from typing import Any, Generic, Type, TypeVar

from google.protobuf import any_pb2, wrappers_pb2
from google.protobuf.message import Message
from ni.pythonpanel.v1 import python_panel_types_pb2

_TPythonType = TypeVar("_TPythonType")
_TProtobufType = TypeVar("_TProtobufType", bound=Message)

_logger = logging.getLogger(__name__)


class Converter(Generic[_TPythonType, _TProtobufType], ABC):
    """A class that defines how to convert between Python objects and protobuf Any messages."""

    @property
    @abstractmethod
    def python_typename(self) -> str:
        """The Python type that this converter handles."""

    @property
    @abstractmethod
    def protobuf_message(self) -> Type[_TProtobufType]:
        """The type-specific protobuf message for the Python type."""

    @property
    def protobuf_typename(self) -> str:
        """The protobuf name for the type."""
        return self.protobuf_message.DESCRIPTOR.full_name  # type: ignore[no-any-return]

    def to_protobuf_any(self, python_value: _TPythonType) -> any_pb2.Any:
        """Convert the Python object to its type-specific message and pack it as any_pb2.Any."""
        message = self.to_protobuf_message(python_value)
        as_any = any_pb2.Any()
        as_any.Pack(message)
        return as_any

    @abstractmethod
    def to_protobuf_message(self, python_value: _TPythonType) -> _TProtobufType:
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


class BoolConverter(Converter[bool, wrappers_pb2.BoolValue]):
    """A converter for boolean types."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return bool.__name__

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.BoolValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.BoolValue

    def to_protobuf_message(self, python_value: bool) -> wrappers_pb2.BoolValue:
        """Convert the Python bool to a protobuf wrappers_pb2.BoolValue."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_value: wrappers_pb2.BoolValue) -> bool:
        """Convert the protobuf message to a Python bool."""
        return protobuf_value.value


class BytesConverter(Converter[bytes, wrappers_pb2.BytesValue]):
    """A converter for byte string types."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return bytes.__name__

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.BytesValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.BytesValue

    def to_protobuf_message(self, python_value: bytes) -> wrappers_pb2.BytesValue:
        """Convert the Python bytes string to a protobuf wrappers_pb2.BytesValue."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_value: wrappers_pb2.BytesValue) -> bytes:
        """Convert the protobuf message to a Python bytes string."""
        return protobuf_value.value


class FloatConverter(Converter[float, wrappers_pb2.DoubleValue]):
    """A converter for floating point types."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return float.__name__

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.DoubleValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.DoubleValue

    def to_protobuf_message(self, python_value: float) -> wrappers_pb2.DoubleValue:
        """Convert the Python float to a protobuf wrappers_pb2.DoubleValue."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_value: wrappers_pb2.DoubleValue) -> float:
        """Convert the protobuf message to a Python float."""
        return protobuf_value.value


class IntConverter(Converter[int, wrappers_pb2.Int64Value]):
    """A converter for integer types."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return int.__name__

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.Int64Value]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.Int64Value

    def to_protobuf_message(self, python_value: int) -> wrappers_pb2.Int64Value:
        """Convert the Python int to a protobuf wrappers_pb2.Int64Value."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_value: wrappers_pb2.Int64Value) -> int:
        """Convert the protobuf message to a Python int."""
        return protobuf_value.value


class StrConverter(Converter[str, wrappers_pb2.StringValue]):
    """A converter for text string types."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return str.__name__

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.StringValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.StringValue

    def to_protobuf_message(self, python_value: str) -> wrappers_pb2.StringValue:
        """Convert the Python str to a protobuf wrappers_pb2.StringValue."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_value: wrappers_pb2.StringValue) -> str:
        """Convert the protobuf message to a Python string."""
        return protobuf_value.value


class BoolCollectionConverter(Converter[Collection[bool], python_panel_types_pb2.BoolCollection]):
    """A converter for a Collection of bools."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{Collection.__name__}.{bool.__name__}"

    @property
    def protobuf_message(self) -> Type[python_panel_types_pb2.BoolCollection]:
        """The type-specific protobuf message for the Python type."""
        return python_panel_types_pb2.BoolCollection

    def to_protobuf_message(self, python_value: Collection[bool]) -> python_panel_types_pb2.BoolCollection:
        """Convert the Python collection of bools to a protobuf python_panel_types_pb2.BoolCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(self, protobuf_value: python_panel_types_pb2.BoolCollection) -> Collection[bool]:
        """Convert the protobuf message to a Python collection of bools."""
        return list(protobuf_value.values)


class BytesCollectionConverter(Converter[Collection[bytes], python_panel_types_pb2.ByteStringCollection]):
    """A converter for a Collection of byte strings."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{Collection.__name__}.{bytes.__name__}"

    @property
    def protobuf_message(self) -> Type[python_panel_types_pb2.ByteStringCollection]:
        """The type-specific protobuf message for the Python type."""
        return python_panel_types_pb2.ByteStringCollection

    def to_protobuf_message(self, python_value: Collection[bytes]) -> python_panel_types_pb2.ByteStringCollection:
        """Convert the Python collection of byte strings to a protobuf python_panel_types_pb2.ByteStringCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(self, protobuf_value: python_panel_types_pb2.ByteStringCollection) -> Collection[bytes]:
        """Convert the protobuf message to a Python collection of byte strings."""
        return list(protobuf_value.values)


class FloatCollectionConverter(Converter[Collection[float], python_panel_types_pb2.FloatCollection]):
    """A converter for a Collection of floats."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{Collection.__name__}.{float.__name__}"

    @property
    def protobuf_message(self) -> Type[python_panel_types_pb2.FloatCollection]:
        """The type-specific protobuf message for the Python type."""
        return python_panel_types_pb2.FloatCollection

    def to_protobuf_message(self, python_value: Collection[float]) -> python_panel_types_pb2.FloatCollection:
        """Convert the Python collection of floats to a protobuf python_panel_types_pb2.FloatCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(self, protobuf_value: python_panel_types_pb2.FloatCollection) -> Collection[float]:
        """Convert the protobuf message to a Python collection of floats."""
        return list(protobuf_value.values)


class IntCollectionConverter(Converter[Collection[int], python_panel_types_pb2.IntCollection]):
    """A converter for a Collection of integers."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{Collection.__name__}.{int.__name__}"

    @property
    def protobuf_message(self) -> Type[python_panel_types_pb2.IntCollection]:
        """The type-specific protobuf message for the Python type."""
        return python_panel_types_pb2.IntCollection

    def to_protobuf_message(self, python_value: Collection[int]) -> python_panel_types_pb2.IntCollection:
        """Convert the Python collection of integers to a protobuf python_panel_types_pb2.IntCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(self, protobuf_value: python_panel_types_pb2.IntCollection) -> Collection[int]:
        """Convert the protobuf message to a Python collection of integers."""
        return list(protobuf_value.values)


class StrCollectionConverter(Converter[Collection[str], python_panel_types_pb2.StringCollection]):
    """A converter for a Collection of strings."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{Collection.__name__}.{str.__name__}"

    @property
    def protobuf_message(self) -> Type[python_panel_types_pb2.StringCollection]:
        """The type-specific protobuf message for the Python type."""
        return python_panel_types_pb2.StringCollection

    def to_protobuf_message(self, python_value: Collection[str]) -> python_panel_types_pb2.StringCollection:
        """Convert the Python collection of strings to a protobuf python_panel_types_pb2.StringCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(self, protobuf_value: python_panel_types_pb2.StringCollection) -> Collection[str]:
        """Convert the protobuf message to a Python collection of strings."""
        return list(protobuf_value.values)


# FFV -- consider adding a RegisterConverter mechanism
_CONVERTIBLE_TYPES: list[Converter[Any, Any]] = [
    # Scalars first
    BoolConverter(),
    BytesConverter(),
    FloatConverter(),
    IntConverter(),
    StrConverter(),
    # Containers next
    BoolCollectionConverter(),
    BytesCollectionConverter(),
    FloatCollectionConverter(),
    IntCollectionConverter(),
    StrCollectionConverter(),
]

_CONVERTIBLE_COLLECTION_TYPES = {
    frozenset,
    list,
    set,
    tuple,
}

_CONVERTER_FOR_PYTHON_TYPE = {entry.python_typename: entry for entry in _CONVERTIBLE_TYPES}
_CONVERTER_FOR_GRPC_TYPE = {entry.protobuf_typename: entry for entry in _CONVERTIBLE_TYPES}
_SUPPORTED_PYTHON_TYPES = _CONVERTER_FOR_PYTHON_TYPE.keys()


def to_any(python_value: object) -> any_pb2.Any:
    """Convert a Python object to a protobuf Any."""
    underlying_parents = type(python_value).mro()  # This covers enum.IntEnum and similar

    container_type = None
    value_is_collection = _CONVERTIBLE_COLLECTION_TYPES.intersection(underlying_parents)
    if value_is_collection:
        # Assume Sized -- Generators not supported, callers must use list(), set(), ... as desired
        if not isinstance(python_value, Collection):
            raise TypeError()
        if len(python_value) == 0:
            underlying_parents = type(None).mro()
        else:
            # Assume homogenous -- collections of mixed-types not supported
            visitor = iter(python_value)
            first_value = next(visitor)
            underlying_parents = type(first_value).mro()
        container_type = Collection

    best_matching_type = None
    candidates = [parent.__name__ for parent in underlying_parents]
    for candidate in candidates:
        python_typename = f"{container_type.__name__}.{candidate}" if container_type else candidate
        if python_typename not in _SUPPORTED_PYTHON_TYPES:
            continue
        best_matching_type = python_typename
        break

    if not best_matching_type:
        payload_type = underlying_parents[0]
        raise TypeError(
            f"Unsupported type: ({container_type}, {payload_type}) with parents {underlying_parents}. Supported types are: {_SUPPORTED_PYTHON_TYPES}"
        )
    _logger.debug(f"Best matching type for '{repr(python_value)}' resolved to {best_matching_type}")

    converter = _CONVERTER_FOR_PYTHON_TYPE[best_matching_type]
    return converter.to_protobuf_any(python_value)


def from_any(protobuf_any: any_pb2.Any) -> object:
    """Convert a protobuf Any to a Python object."""
    if not isinstance(protobuf_any, any_pb2.Any):
        raise ValueError(f"Unexpected type: {type(protobuf_any)}")

    underlying_typename = protobuf_any.TypeName()
    _logger.debug(f"Unpacking type '{underlying_typename}'")

    converter = _CONVERTER_FOR_GRPC_TYPE[underlying_typename]
    return converter.to_python(protobuf_any)
