"""Classes to convert between builtin Python scalars and containers."""

import datetime as dt
from collections.abc import Collection
from typing import Type

from google.protobuf import duration_pb2, timestamp_pb2, wrappers_pb2
from ni.panels.v1 import panel_types_pb2

from nipanel.converters import Converter


class BoolConverter(Converter[bool, wrappers_pb2.BoolValue]):
    """A converter for boolean types."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{bool.__module__}.{bool.__name__}"

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.BoolValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.BoolValue

    def to_protobuf_message(self, python_value: bool) -> wrappers_pb2.BoolValue:
        """Convert the Python bool to a protobuf wrappers_pb2.BoolValue."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_message: wrappers_pb2.BoolValue) -> bool:
        """Convert the protobuf message to a Python bool."""
        return protobuf_message.value


class BytesConverter(Converter[bytes, wrappers_pb2.BytesValue]):
    """A converter for byte string types."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{bytes.__module__}.{bytes.__name__}"

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.BytesValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.BytesValue

    def to_protobuf_message(self, python_value: bytes) -> wrappers_pb2.BytesValue:
        """Convert the Python bytes string to a protobuf wrappers_pb2.BytesValue."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_message: wrappers_pb2.BytesValue) -> bytes:
        """Convert the protobuf message to a Python bytes string."""
        return protobuf_message.value


class FloatConverter(Converter[float, wrappers_pb2.DoubleValue]):
    """A converter for floating point types."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{float.__module__}.{float.__name__}"

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.DoubleValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.DoubleValue

    def to_protobuf_message(self, python_value: float) -> wrappers_pb2.DoubleValue:
        """Convert the Python float to a protobuf wrappers_pb2.DoubleValue."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_message: wrappers_pb2.DoubleValue) -> float:
        """Convert the protobuf message to a Python float."""
        return protobuf_message.value


class IntConverter(Converter[int, wrappers_pb2.Int64Value]):
    """A converter for integer types."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{int.__module__}.{int.__name__}"

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.Int64Value]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.Int64Value

    def to_protobuf_message(self, python_value: int) -> wrappers_pb2.Int64Value:
        """Convert the Python int to a protobuf wrappers_pb2.Int64Value."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_message: wrappers_pb2.Int64Value) -> int:
        """Convert the protobuf message to a Python int."""
        return protobuf_message.value


class StrConverter(Converter[str, wrappers_pb2.StringValue]):
    """A converter for text string types."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{str.__module__}.{str.__name__}"

    @property
    def protobuf_message(self) -> Type[wrappers_pb2.StringValue]:
        """The type-specific protobuf message for the Python type."""
        return wrappers_pb2.StringValue

    def to_protobuf_message(self, python_value: str) -> wrappers_pb2.StringValue:
        """Convert the Python str to a protobuf wrappers_pb2.StringValue."""
        return self.protobuf_message(value=python_value)

    def to_python_value(self, protobuf_message: wrappers_pb2.StringValue) -> str:
        """Convert the protobuf message to a Python string."""
        return protobuf_message.value


class DTDateTimeConverter(Converter[dt.datetime, timestamp_pb2.Timestamp]):
    """A converter for datetime.datetime types."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{dt.datetime.__module__}.{dt.datetime.__name__}"

    @property
    def protobuf_message(self) -> Type[timestamp_pb2.Timestamp]:
        """The type-specific protobuf message for the Python type."""
        return timestamp_pb2.Timestamp

    def to_protobuf_message(self, python_value: dt.datetime) -> timestamp_pb2.Timestamp:
        """Convert the Python dt.datetime to a protobuf timestamp_pb2.Timestamp."""
        ts = self.protobuf_message()
        ts.FromDatetime(python_value)
        return ts

    def to_python_value(self, protobuf_message: timestamp_pb2.Timestamp) -> dt.datetime:
        """Convert the protobuf timestamp_pb2.Timestamp to a Python dt.datetime."""
        return protobuf_message.ToDatetime()


class DTTimeDeltaConverter(Converter[dt.timedelta, duration_pb2.Duration]):
    """A converter for datetime.timedelta types."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{dt.timedelta.__module__}.{dt.timedelta.__name__}"

    @property
    def protobuf_message(self) -> Type[duration_pb2.Duration]:
        """The type-specific protobuf message for the Python type."""
        return duration_pb2.Duration

    def to_protobuf_message(self, python_value: dt.timedelta) -> duration_pb2.Duration:
        """Convert the Python dt.timedelta to a protobuf duration_pb2.Duration."""
        dur = self.protobuf_message()
        dur.FromTimedelta(python_value)
        return dur

    def to_python_value(self, protobuf_message: duration_pb2.Duration) -> dt.timedelta:
        """Convert the protobuf timestamp_pb2.Timestamp to a Python dt.timedelta."""
        return protobuf_message.ToTimedelta()


class BoolCollectionConverter(Converter[Collection[bool], panel_types_pb2.BoolCollection]):
    """A converter for a Collection of bools."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{Collection.__name__}.{bool.__module__}.{bool.__name__}"

    @property
    def protobuf_message(self) -> Type[panel_types_pb2.BoolCollection]:
        """The type-specific protobuf message for the Python type."""
        return panel_types_pb2.BoolCollection

    def to_protobuf_message(self, python_value: Collection[bool]) -> panel_types_pb2.BoolCollection:
        """Convert the collection of bools to panel_types_pb2.BoolCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(self, protobuf_message: panel_types_pb2.BoolCollection) -> Collection[bool]:
        """Convert the protobuf message to a Python collection of bools."""
        return list(protobuf_message.values)


class BytesCollectionConverter(Converter[Collection[bytes], panel_types_pb2.ByteStringCollection]):
    """A converter for a Collection of byte strings."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{Collection.__name__}.{bytes.__module__}.{bytes.__name__}"

    @property
    def protobuf_message(self) -> Type[panel_types_pb2.ByteStringCollection]:
        """The type-specific protobuf message for the Python type."""
        return panel_types_pb2.ByteStringCollection

    def to_protobuf_message(
        self, python_value: Collection[bytes]
    ) -> panel_types_pb2.ByteStringCollection:
        """Convert the collection of byte strings to panel_types_pb2.ByteStringCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(
        self, protobuf_message: panel_types_pb2.ByteStringCollection
    ) -> Collection[bytes]:
        """Convert the protobuf message to a Python collection of byte strings."""
        return list(protobuf_message.values)


class FloatCollectionConverter(Converter[Collection[float], panel_types_pb2.FloatCollection]):
    """A converter for a Collection of floats."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{Collection.__name__}.{float.__module__}.{float.__name__}"

    @property
    def protobuf_message(self) -> Type[panel_types_pb2.FloatCollection]:
        """The type-specific protobuf message for the Python type."""
        return panel_types_pb2.FloatCollection

    def to_protobuf_message(
        self, python_value: Collection[float]
    ) -> panel_types_pb2.FloatCollection:
        """Convert the collection of floats to panel_types_pb2.FloatCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(
        self, protobuf_message: panel_types_pb2.FloatCollection
    ) -> Collection[float]:
        """Convert the protobuf message to a Python collection of floats."""
        return list(protobuf_message.values)


class IntCollectionConverter(Converter[Collection[int], panel_types_pb2.IntCollection]):
    """A converter for a Collection of integers."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{Collection.__name__}.{int.__module__}.{int.__name__}"

    @property
    def protobuf_message(self) -> Type[panel_types_pb2.IntCollection]:
        """The type-specific protobuf message for the Python type."""
        return panel_types_pb2.IntCollection

    def to_protobuf_message(self, python_value: Collection[int]) -> panel_types_pb2.IntCollection:
        """Convert the collection of integers to panel_types_pb2.IntCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(self, protobuf_message: panel_types_pb2.IntCollection) -> Collection[int]:
        """Convert the protobuf message to a Python collection of integers."""
        return list(protobuf_message.values)


class StrCollectionConverter(Converter[Collection[str], panel_types_pb2.StringCollection]):
    """A converter for a Collection of strings."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{Collection.__name__}.{str.__module__}.{str.__name__}"

    @property
    def protobuf_message(self) -> Type[panel_types_pb2.StringCollection]:
        """The type-specific protobuf message for the Python type."""
        return panel_types_pb2.StringCollection

    def to_protobuf_message(
        self, python_value: Collection[str]
    ) -> panel_types_pb2.StringCollection:
        """Convert the collection of strings to panel_types_pb2.StringCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(
        self, protobuf_message: panel_types_pb2.StringCollection
    ) -> Collection[str]:
        """Convert the protobuf message to a Python collection of strings."""
        return list(protobuf_message.values)
