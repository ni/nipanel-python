"""Classes to convert between measurement specific protobuf types and containers."""

from __future__ import annotations

from collections.abc import Collection
from typing import Any, Type, Union

import hightime as ht
import nitypes.bintime as bt
import numpy as np
from ni.protobuf.types import (
    array_pb2,
    precision_duration_pb2,
    precision_duration_conversion,
    precision_timestamp_pb2,
    precision_timestamp_conversion,
    scalar_conversion,
    scalar_pb2,
    vector_pb2,
    vector_conversion,
    waveform_conversion,
    waveform_pb2,
)
from nitypes.complex import ComplexInt32Base
from nitypes.scalar import Scalar
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum
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

    def to_protobuf_message(self, python_value: Collection[bytes]) -> array_pb2.BytesArray:
        """Convert the collection of byte strings to array_pb2.BytesArray."""
        return self.protobuf_message(values=python_value)

    def to_python_value(self, protobuf_message: array_pb2.BytesArray) -> Collection[bytes]:
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

    def to_protobuf_message(self, python_value: Collection[float]) -> array_pb2.DoubleArray:
        """Convert the collection of floats to array_pb2.DoubleArray."""
        return self.protobuf_message(values=python_value)

    def to_python_value(self, protobuf_message: array_pb2.DoubleArray) -> Collection[float]:
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

    def to_protobuf_message(self, python_value: Collection[str]) -> array_pb2.StringArray:
        """Convert the collection of strings to array_pb2.StringCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(self, protobuf_message: array_pb2.StringArray) -> Collection[str]:
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

    def to_protobuf_message(
        self, python_value: Collection[Collection[float]]
    ) -> array_pb2.Double2DArray:
        """Convert the Python Collection[Collection[float]] to a protobuf Double2DArray."""
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

    def to_python_value(
        self, protobuf_message: array_pb2.Double2DArray
    ) -> Collection[Collection[float]]:
        """Convert the protobuf Double2DArray to a Python Collection[Collection[float]]."""
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


class DoubleAnalogWaveformConverter(
    Converter[AnalogWaveform[np.float64], waveform_pb2.DoubleAnalogWaveform]
):
    """A converter for AnalogWaveform types with double-precision data."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return AnalogWaveform

    @property
    def python_typename(self) -> str:
        """The Python type name that this converter handles."""
        base_typename = super().python_typename
        return f"{base_typename}[float64]"

    @property
    def protobuf_message(self) -> Type[waveform_pb2.DoubleAnalogWaveform]:
        """The type-specific protobuf message for the Python type."""
        return waveform_pb2.DoubleAnalogWaveform

    def to_protobuf_message(
        self, python_value: AnalogWaveform[np.float64]
    ) -> waveform_pb2.DoubleAnalogWaveform:
        """Convert the Python AnalogWaveform to a protobuf DoubleAnalogWaveform."""
        return waveform_conversion.float64_analog_waveform_to_protobuf(python_value)

    def to_python_value(
        self, protobuf_message: waveform_pb2.DoubleAnalogWaveform
    ) -> AnalogWaveform[np.float64]:
        """Convert the protobuf DoubleAnalogWaveform to a Python AnalogWaveform."""
        return waveform_conversion.float64_analog_waveform_from_protobuf(protobuf_message)


class Int16AnalogWaveformConverter(
    Converter[AnalogWaveform[np.int16], waveform_pb2.I16AnalogWaveform]
):
    """A converter for AnalogWaveform types with 16-bit integer data."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return AnalogWaveform

    @property
    def python_typename(self) -> str:
        """The Python type name that this converter handles."""
        base_typename = super().python_typename
        return f"{base_typename}[int16]"

    @property
    def protobuf_message(self) -> Type[waveform_pb2.I16AnalogWaveform]:
        """The type-specific protobuf message for the Python type."""
        return waveform_pb2.I16AnalogWaveform

    def to_protobuf_message(
        self, python_value: AnalogWaveform[np.int16]
    ) -> waveform_pb2.I16AnalogWaveform:
        """Convert the Python AnalogWaveform to a protobuf Int16AnalogWaveformConverter."""
        return waveform_conversion.int16_analog_waveform_to_protobuf(python_value)

    def to_python_value(
        self, protobuf_message: waveform_pb2.I16AnalogWaveform
    ) -> AnalogWaveform[np.int16]:
        """Convert the protobuf Int16AnalogWaveformConverter to a Python AnalogWaveform."""
        return waveform_conversion.int16_analog_waveform_from_protobuf(protobuf_message)


class DoubleComplexWaveformConverter(
    Converter[ComplexWaveform[np.complex128], waveform_pb2.DoubleComplexWaveform]
):
    """A converter for complex waveform types with 64-bit real and imaginary data."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return ComplexWaveform

    @property
    def python_typename(self) -> str:
        """The Python type name that this converter handles."""
        base_typename = super().python_typename
        return f"{base_typename}[complex128]"

    @property
    def protobuf_message(self) -> Type[waveform_pb2.DoubleComplexWaveform]:
        """The type-specific protobuf message for the Python type."""
        return waveform_pb2.DoubleComplexWaveform

    def to_protobuf_message(
        self, python_value: ComplexWaveform[np.complex128]
    ) -> waveform_pb2.DoubleComplexWaveform:
        """Convert the Python ComplexWaveform to a protobuf DoubleComplexWaveform."""
        return waveform_conversion.float64_complex_waveform_to_protobuf(python_value)

    def to_python_value(
        self, protobuf_message: waveform_pb2.DoubleComplexWaveform
    ) -> ComplexWaveform[np.complex128]:
        """Convert the protobuf DoubleComplexWaveform to a Python ComplexWaveform."""
        return waveform_conversion.float64_complex_waveform_from_protobuf(protobuf_message)


class Int16ComplexWaveformConverter(
    Converter[ComplexWaveform[ComplexInt32Base], waveform_pb2.I16ComplexWaveform]
):
    """A converter for complex waveform types with 16-bit real and imaginary data."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return ComplexWaveform

    @property
    def python_typename(self) -> str:
        """The Python type name that this converter handles."""
        base_typename = super().python_typename
        # Use the string representation of ComplexInt32DType
        return f"{base_typename}[[('real', '<i2'), ('imag', '<i2')]]"

    @property
    def protobuf_message(self) -> Type[waveform_pb2.I16ComplexWaveform]:
        """The type-specific protobuf message for the Python type."""
        return waveform_pb2.I16ComplexWaveform

    def to_protobuf_message(
        self, python_value: ComplexWaveform[ComplexInt32Base]
    ) -> waveform_pb2.I16ComplexWaveform:
        """Convert the Python ComplexWaveform to a protobuf I16ComplexWaveform."""
        return waveform_conversion.int16_complex_waveform_to_protobuf(python_value)

    def to_python_value(
        self, protobuf_message: waveform_pb2.I16ComplexWaveform
    ) -> ComplexWaveform[ComplexInt32Base]:
        """Convert the protobuf I16ComplexWaveform to a Python ComplexWaveform."""
        return waveform_conversion.int16_complex_waveform_from_protobuf(protobuf_message)


class DigitalWaveformConverter(Converter[DigitalWaveform[Any], waveform_pb2.DigitalWaveform]):
    """A converter for digital waveform types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return DigitalWaveform

    @property
    def protobuf_message(self) -> Type[waveform_pb2.DigitalWaveform]:
        """The type-specific protobuf message for the Python type."""
        return waveform_pb2.DigitalWaveform

    def to_protobuf_message(
        self, python_value: DigitalWaveform[Any]
    ) -> waveform_pb2.DigitalWaveform:
        """Convert the Python DigitalWaveform to a protobuf DigitalWaveform."""
        return waveform_conversion.digital_waveform_to_protobuf(python_value)

    def to_python_value(
        self, protobuf_message: waveform_pb2.DigitalWaveform
    ) -> DigitalWaveform[Any]:
        """Convert the protobuf DigitalWaveform to a Python DigitalWaveform."""
        return waveform_conversion.digital_waveform_from_protobuf(protobuf_message)


class DoubleSpectrumConverter(Converter[Spectrum[np.float64], waveform_pb2.DoubleSpectrum]):
    """A converter for spectrums with float64 data."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return Spectrum

    @property
    def protobuf_message(self) -> Type[waveform_pb2.DoubleSpectrum]:
        """The type-specific protobuf message for the Python type."""
        return waveform_pb2.DoubleSpectrum

    def to_protobuf_message(
        self, python_value: Spectrum[np.float64]
    ) -> waveform_pb2.DoubleSpectrum:
        """Convert the Python Spectrum to a protobuf DoubleSpectrum."""
        return waveform_conversion.float64_spectrum_to_protobuf(python_value)

    def to_python_value(
        self, protobuf_message: waveform_pb2.DoubleSpectrum
    ) -> Spectrum[np.float64]:
        """Convert the protobuf DoubleSpectrum to a Python Spectrum."""
        return waveform_conversion.float64_spectrum_from_protobuf(protobuf_message)


class BTDateTimeConverter(Converter[bt.DateTime, precision_timestamp_pb2.PrecisionTimestamp]):
    """A converter for bintime.DateTime types.

    .. note:: The nipanel package will always convert PrecisionTimestamp messages to
        hightime.datetime objects using HTDateTimeConverter. To use bintime.DateTime
        values in a panel, you must pass a bintime.DateTime value for the default_value
        parameter of the get_value() method on the panel.
    """

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return bt.DateTime

    @property
    def protobuf_message(self) -> Type[precision_timestamp_pb2.PrecisionTimestamp]:
        """The type-specific protobuf message for the Python type."""
        return precision_timestamp_pb2.PrecisionTimestamp

    @property
    def protobuf_typename(self) -> str:
        """The protobuf name for the type."""
        # Override the base class here because there can only be one converter that
        # converts PrecisionTimestamp objects. Since there are two converters that convert
        # to PrecisionTimestamp, we have to choose one to handle conversion from protobuf.
        # For the purposes of nipanel, we'll convert PrecisionTimestamp messages to
        # hightime.datetime. See HTDateTimeConverter.
        return "PrecisionTimestamp_Placeholder"

    def to_protobuf_message(
        self, python_value: bt.DateTime
    ) -> precision_timestamp_pb2.PrecisionTimestamp:
        """Convert the Python DateTime to a protobuf PrecisionTimestamp."""
        return precision_timestamp_conversion.bintime_datetime_to_protobuf(python_value)

    def to_python_value(
        self, protobuf_message: precision_timestamp_pb2.PrecisionTimestamp
    ) -> bt.DateTime:
        """Convert the protobuf PrecisionTimestamp to a Python DateTime."""
        return precision_timestamp_conversion.bintime_datetime_from_protobuf(protobuf_message)


class BTTimeDeltaConverter(Converter[bt.TimeDelta, precision_duration_pb2.PrecisionDuration]):
    """A converter for bintime.TimeDelta types.

    .. note:: The nipanel package will always convert PrecisionDuration messages to
        hightime.timedelta objects using HTTimeDeltaConverter. To use bintime.TimeDelta
        values in a panel, you must pass a bintime.TimeDelta value for the default_value
        parameter of the get_value() method on the panel.
    """

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return bt.TimeDelta

    @property
    def protobuf_message(self) -> Type[precision_duration_pb2.PrecisionDuration]:
        """The type-specific protobuf message for the Python type."""
        return precision_duration_pb2.PrecisionDuration

    @property
    def protobuf_typename(self) -> str:
        """The protobuf name for the type."""
        # Override the base class here because there can only be one converter that
        # converts PrecisionDuration objects. Since there are two converters that convert
        # to PrecisionDuration, we have to choose one to handle conversion from protobuf.
        # For the purposes of nipanel, we'll convert PrecisionDuration messages to
        # hightime.timedelta. See HTTimeDeltaConverter.
        return "PrecisionDuration_Placeholder"

    def to_protobuf_message(
        self, python_value: bt.TimeDelta
    ) -> precision_duration_pb2.PrecisionDuration:
        """Convert the Python TimeDelta to a protobuf PrecisionDuration."""
        return precision_duration_conversion.bintime_timedelta_to_protobuf(python_value)

    def to_python_value(
        self, protobuf_message: precision_duration_pb2.PrecisionDuration
    ) -> bt.TimeDelta:
        """Convert the protobuf PrecisionDuration to a Python TimeDelta."""
        return precision_duration_conversion.bintime_timedelta_from_protobuf(protobuf_message)


class HTDateTimeConverter(Converter[ht.datetime, precision_timestamp_pb2.PrecisionTimestamp]):
    """A converter for hightime.datetime objects."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return ht.datetime

    @property
    def protobuf_message(self) -> Type[precision_timestamp_pb2.PrecisionTimestamp]:
        """The type-specific protobuf message for the Python type."""
        return precision_timestamp_pb2.PrecisionTimestamp

    def to_protobuf_message(
        self, python_value: ht.datetime
    ) -> precision_timestamp_pb2.PrecisionTimestamp:
        """Convert the Python DateTime to a protobuf PrecisionTimestamp."""
        return precision_timestamp_conversion.hightime_datetime_to_protobuf(python_value)

    def to_python_value(
        self, protobuf_message: precision_timestamp_pb2.PrecisionTimestamp
    ) -> ht.datetime:
        """Convert the protobuf PrecisionTimestamp to a Python DateTime."""
        return precision_timestamp_conversion.hightime_datetime_from_protobuf(protobuf_message)


class HTTimeDeltaConverter(Converter[ht.timedelta, precision_duration_pb2.PrecisionDuration]):
    """A converter for hightime.timedelta objects."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return ht.timedelta

    @property
    def protobuf_message(self) -> Type[precision_duration_pb2.PrecisionDuration]:
        """The type-specific protobuf message for the Python type."""
        return precision_duration_pb2.PrecisionDuration

    def to_protobuf_message(
        self, python_value: ht.timedelta
    ) -> precision_duration_pb2.PrecisionDuration:
        """Convert the Python timedelta to a protobuf PrecisionDuration."""
        return precision_duration_conversion.hightime_timedelta_to_protobuf(python_value)

    def to_python_value(
        self, protobuf_message: precision_duration_pb2.PrecisionDuration
    ) -> ht.timedelta:
        """Convert the protobuf PrecisionDuration to a Python timedelta."""
        return precision_duration_conversion.hightime_timedelta_from_protobuf(protobuf_message)


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
        return scalar_conversion.scalar_to_protobuf(python_value)

    def to_python_value(self, protobuf_message: scalar_pb2.Scalar) -> Scalar[_AnyScalarType]:
        """Convert the protobuf message to a Python Scalar."""
        return scalar_conversion.scalar_from_protobuf(protobuf_message)


class VectorConverter(Converter[Vector[_AnyScalarType], vector_pb2.Vector]):
    """A converter for Vector objects."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return Vector

    @property
    def protobuf_message(self) -> Type[vector_pb2.Vector]:
        """The type-specific protobuf message for the Python type."""
        return vector_pb2.Vector

    def to_protobuf_message(self, python_value: Vector[Any]) -> vector_pb2.Vector:
        """Convert the Python Vector to a protobuf vector_pb2.Vector."""
        return vector_conversion.vector_to_protobuf(python_value)

    def to_python_value(self, protobuf_message: vector_pb2.Vector) -> Vector[_AnyScalarType]:
        """Convert the protobuf message to a Python Vector."""
        return vector_conversion.vector_from_protobuf(protobuf_message)
