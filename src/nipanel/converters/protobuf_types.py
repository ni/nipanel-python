"""Classes to convert between measurement specific protobuf types and containers."""

from __future__ import annotations

from collections.abc import Collection
from typing import Type, Union

import nitypes.bintime as bt
import numpy as np
from ni.protobuf.types import attribute_value_pb2, scalar_pb2, array_pb2
from ni.protobuf.types.precision_timestamp_pb2 import PrecisionTimestamp
from ni.protobuf.types.scalar_conversion import scalar_from_protobuf, scalar_to_protobuf
from ni.protobuf.types.precision_timestamp_conversion import (
    bintime_datetime_from_protobuf,
    bintime_datetime_to_protobuf,
)
from ni.protobuf.types.waveform_conversion import (
    float64_analog_waveform_from_protobuf,
    float64_analog_waveform_to_protobuf,
)
from ni.protobuf.types.waveform_pb2 import DoubleAnalogWaveform
from nitypes.scalar import Scalar
from nitypes.waveform import AnalogWaveform
from typing_extensions import TypeAlias

from nipanel.converters import Converter, CollectionConverter, CollectionConverter2D

_AnyScalarType: TypeAlias = Union[bool, int, float, str]


class BoolCollectionConverter(CollectionConverter[bool, array_pb2.BoolArray]):
    """A converter for a Collection of bools."""

    @property
    def item_type(self) -> type:
        """The Python type that this converter handles."""
        return bool

    @property
    def protobuf_message(self) -> Type[array_pb2.BoolArray]:
        """The type-specific protobuf message for the Python type."""
        return array_pb2.BoolArray

    def to_protobuf_message(self, python_value: Collection[bool]) -> array_pb2.BoolArray:
        """Convert the collection of bools to array_pb2.BoolArray."""
        return self.protobuf_message(values=python_value)

    def to_python_value(self, protobuf_message: array_pb2.BoolArray) -> Collection[bool]:
        """Convert the protobuf message to a Python collection of bools."""
        return list(protobuf_message.values)


class BytesCollectionConverter(CollectionConverter[bytes, array_pb2.BytesArray]):
    """A converter for a Collection of byte strings."""

    @property
    def item_type(self) -> type:
        """The Python type that this converter handles."""
        return bytes

    @property
    def protobuf_message(self) -> Type[array_pb2.BytesArray]:
        """The type-specific protobuf message for the Python type."""
        return array_pb2.BytesArray

    def to_protobuf_message(
        self, python_value: Collection[bytes]
    ) -> array_pb2.BytesArray:
        """Convert the collection of byte strings to array_pb2.BytesArray."""
        return self.protobuf_message(values=python_value)

    def to_python_value(
        self, protobuf_message: array_pb2.BytesArray
    ) -> Collection[bytes]:
        """Convert the protobuf message to a Python collection of byte strings."""
        return list(protobuf_message.values)


class FloatCollectionConverter(CollectionConverter[float, array_pb2.DoubleArray]):
    """A converter for a Collection of floats."""

    @property
    def item_type(self) -> type:
        """The Python type that this converter handles."""
        return float

    @property
    def protobuf_message(self) -> Type[array_pb2.DoubleArray]:
        """The type-specific protobuf message for the Python type."""
        return array_pb2.DoubleArray

    def to_protobuf_message(
        self, python_value: Collection[float]
    ) -> array_pb2.DoubleArray:
        """Convert the collection of floats to array_pb2.DoubleArray."""
        return self.protobuf_message(values=python_value)

    def to_python_value(
        self, protobuf_message: array_pb2.DoubleArray
    ) -> Collection[float]:
        """Convert the protobuf message to a Python collection of floats."""
        return list(protobuf_message.values)


class IntCollectionConverter(CollectionConverter[int, array_pb2.SInt64Array]):
    """A converter for a Collection of integers."""

    @property
    def item_type(self) -> type:
        """The Python type that this converter handles."""
        return int

    @property
    def protobuf_message(self) -> Type[array_pb2.SInt64Array]:
        """The type-specific protobuf message for the Python type."""
        return array_pb2.SInt64Array

    def to_protobuf_message(self, python_value: Collection[int]) -> array_pb2.SInt64Array:
        """Convert the collection of integers to array_pb2.SInt64Array."""
        return self.protobuf_message(values=python_value)

    def to_python_value(self, protobuf_message: array_pb2.SInt64Array) -> Collection[int]:
        """Convert the protobuf message to a Python collection of integers."""
        return list(protobuf_message.values)


class StrCollectionConverter(CollectionConverter[str, array_pb2.StringArray]):
    """A converter for a Collection of strings."""

    @property
    def item_type(self) -> type:
        """The Python type that this converter handles."""
        return str

    @property
    def protobuf_message(self) -> Type[array_pb2.StringArray]:
        """The type-specific protobuf message for the Python type."""
        return array_pb2.StringArray

    def to_protobuf_message(
        self, python_value: Collection[str]
    ) -> array_pb2.StringArray:
        """Convert the collection of strings to panel_types_pb2.StringCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(
        self, protobuf_message: array_pb2.StringArray
    ) -> Collection[str]:
        """Convert the protobuf message to a Python collection of strings."""
        return list(protobuf_message.values)



class Double2DArrayConverter(CollectionConverter2D[float, array_pb2.Double2DArray]):
    """A converter between Collection[Collection[float]] and Double2DArray."""

    @property
    def item_type(self) -> type:
        """The Python item type that this converter handles."""
        return float

    @property
    def protobuf_message(self) -> Type[array_pb2.Double2DArray]:
        """The type-specific protobuf message for the Python type."""
        return array_pb2.Double2DArray

    def to_protobuf_message(self, python_value: Collection[Collection[float]]) -> array_pb2.Double2DArray:
        """Convert the Python Collection[Collection[float]] to a protobuf array_pb2.Double2DArray."""
        rows = len(python_value)
        if rows:
            visitor = iter(python_value)
            first_subcollection = next(visitor)
            columns = len(first_subcollection)
        else:
            columns = 0
        if not all(len(subcollection) == columns for subcollection in python_value):
            raise ValueError("All subcollections must have the same length.")

        # Create a flat list in row major order.
        flat_list = [item for subcollection in python_value for item in subcollection]
        return array_pb2.Double2DArray(rows=rows, columns=columns, data=flat_list)

    def to_python_value(self, protobuf_message: array_pb2.Double2DArray) -> Collection[Collection[float]]:
        """Convert the protobuf array_pb2.Double2DArray to a Python Collection[Collection[float]]."""
        if not protobuf_message.data:
            return []
        if len(protobuf_message.data) % protobuf_message.columns != 0:
            raise ValueError("The length of the data list must be divisible by num columns.")

        # Convert from a flat list in row major order into a list of lists.
        list_of_lists = []
        for i in range(0, len(protobuf_message.data), protobuf_message.columns):
            row = protobuf_message.data[i : i + protobuf_message.columns]
            list_of_lists.append(row)

        return list_of_lists


class DoubleAnalogWaveformConverter(Converter[AnalogWaveform[np.float64], DoubleAnalogWaveform]):
    """A converter for AnalogWaveform types with scaled data (double)."""

    def __init__(self) -> None:
        """Initialize a DoubleAnalogWaveformConverter object."""
        self._pt_converter = PrecisionTimestampConverter()

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return AnalogWaveform

    @property
    def protobuf_message(self) -> Type[DoubleAnalogWaveform]:
        """The type-specific protobuf message for the Python type."""
        return DoubleAnalogWaveform

    def to_protobuf_message(self, python_value: AnalogWaveform[np.float64]) -> DoubleAnalogWaveform:
        """Convert the Python AnalogWaveform to a protobuf DoubleAnalogWaveform."""
        return float64_analog_waveform_to_protobuf(python_value)

    def to_python_value(self, protobuf_message: DoubleAnalogWaveform) -> AnalogWaveform[np.float64]:
        """Convert the protobuf DoubleAnalogWaveform to a Python AnalogWaveform."""
        return float64_analog_waveform_from_protobuf(protobuf_message)


class PrecisionTimestampConverter(Converter[bt.DateTime, PrecisionTimestamp]):
    """A converter for bintime.DateTime types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return bt.DateTime

    @property
    def protobuf_message(self) -> Type[PrecisionTimestamp]:
        """The type-specific protobuf message for the Python type."""
        return PrecisionTimestamp

    def to_protobuf_message(self, python_value: bt.DateTime) -> PrecisionTimestamp:
        """Convert the Python DateTime to a protobuf PrecisionTimestamp."""
        return bintime_datetime_to_protobuf(python_value)

    def to_python_value(self, protobuf_message: PrecisionTimestamp) -> bt.DateTime:
        """Convert the protobuf PrecisionTimestamp to a Python DateTime."""
        return bintime_datetime_from_protobuf(protobuf_message)


class ScalarConverter(Converter[Scalar[_AnyScalarType], scalar_pb2.Scalar]):
    """A converter for Scalar objects."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return Scalar

    @property
    def protobuf_message(self) -> Type[scalar_pb2.Scalar]:
        """The type-specific protobuf message for the Python type."""
        return scalar_pb2.Scalar

    def to_protobuf_message(self, python_value: Scalar[_AnyScalarType]) -> scalar_pb2.Scalar:
        """Convert the Python Scalar to a protobuf scalar_pb2.Scalar."""
        return scalar_to_protobuf(python_value)

    def to_python_value(self, protobuf_message: scalar_pb2.Scalar) -> Scalar[_AnyScalarType]:
        """Convert the protobuf message to a Python Scalar."""
        return scalar_from_protobuf(protobuf_message)
