"""Functions and classes to convert types between Python and protobuf."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection
from typing import Generic, Type, TypeVar

from google.protobuf import any_pb2
from google.protobuf.message import Message

_TItemType = TypeVar("_TItemType")
_TPythonType = TypeVar("_TPythonType")
_TProtobufType = TypeVar("_TProtobufType", bound=Message)


class Converter(Generic[_TPythonType, _TProtobufType], ABC):
    """A class that defines how to convert between Python objects and protobuf Any messages."""

    @property
    @abstractmethod
    def python_type(self) -> type:
        """The Python type that this converter handles."""

    @property
    def python_typename(self) -> str:
        """The Python type name that this converter handles."""
        return f"{self.python_type.__module__}.{self.python_type.__name__}"

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


class CollectionConverter(
    Generic[_TItemType, _TProtobufType],
    Converter[Collection[_TItemType], _TProtobufType],
    ABC,
):
    """A converter between a collection of Python objects and protobuf Any messages."""

    @property
    @abstractmethod
    def item_type(self) -> type:
        """The Python item type that this converter handles."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return Collection

    @property
    def python_typename(self) -> str:
        """The Python type name that this converter handles."""
        return "{}[{}]".format(
            f"{Collection.__module__}.{Collection.__name__}",
            f"{self.item_type.__module__}.{self.item_type.__name__}",
        )


class CollectionConverter2D(
    Generic[_TItemType, _TProtobufType],
    Converter[Collection[Collection[_TItemType]], _TProtobufType],
    ABC,
):
    """A converter between a 2D collection of Python objects and protobuf Any messages."""

    @property
    @abstractmethod
    def item_type(self) -> type:
        """The Python item type that this converter handles."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return Collection

    @property
    def python_typename(self) -> str:
        """The Python type name that this converter handles."""
        return "{}[{}[{}]]".format(
            f"{Collection.__module__}.{Collection.__name__}",
            f"{Collection.__module__}.{Collection.__name__}",
            f"{self.item_type.__module__}.{self.item_type.__name__}",
        )
