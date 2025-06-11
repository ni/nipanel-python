"""Classes to convert between builtin Python scalars and containers."""

from collections.abc import Collection
from typing import Any, Type

from google.protobuf import wrappers_pb2
from ni.pythonpanel.v1 import python_panel_types_pb2

from nipanel.converters import Converter

from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.waveform_pb2 import DoubleAnalogWaveform, WaveformAttributeValue
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.precision_timestamp_pb2 import PrecisionTimestamp
from nitypes.waveform import AnalogWaveform
from nitypes.bintime import TimeDelta, DateTime
import numpy


class DoubleAnalogWaveformConverter(Converter[bool, wrappers_pb2.BoolValue]):
    """A converter for AnalogWaveform types with scaled data (double)."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return AnalogWaveform.__name__

    @property
    def protobuf_message(self) -> Type[DoubleAnalogWaveform]:
        """The type-specific protobuf message for the Python type."""
        return DoubleAnalogWaveform

    def to_protobuf_message(self, python_value: AnalogWaveform) -> DoubleAnalogWaveform:
        """Convert the Python bool to a protobuf wrappers_pb2.BoolValue."""
        attributes = []
        for key, value in python_value.extended_properties:
            attr_value = WaveformAttributeValue()
            if isinstance(value, bool):
                attr_value.bool_value = value
            elif isinstance(value, int):
                attr_value.integer_value = value
            elif isinstance(value, float):
                attr_value.double_value = value
            elif isinstance(value, str):
                attr_value.string_value = value
            else:
                raise TypeError(f"Unexpected type for extended property value {type(value)}")

            attributes[key] = attr_value

        return self.protobuf_message(
            t0=python_value.timing.start_time,  # Types don't match
            dt=python_value.timing.sample_interval.total_seconds(),
            y_data=python_value.scaled_data,
            attributes=attributes,
        )

    def to_python_value(self, protobuf_value: DoubleAnalogWaveform) -> AnalogWaveform:
        """Convert the protobuf message to a Python bool."""
        return AnalogWaveform(
            sample_count=protobuf_value.y_data.count(),
            dtype=numpy.float64,
            raw_data=protobuf_value.y_data,
            start_index=0,
            capacity=protobuf_value.y_data.count(),
            extended_properties=protobuf_value.attributes,  # Types don't match
            copy_extended_properties=True,
            timing=None,  # TODO
            scale_mode=None,  # TODO
        )


class PrecisionTimestampConverter(Converter[bytes, wrappers_pb2.BytesValue]):
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

    def to_protobuf_message(
        self, python_value: Collection[bool]
    ) -> python_panel_types_pb2.BoolCollection:
        """Convert the collection of bools to python_panel_types_pb2.BoolCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(
        self, protobuf_value: python_panel_types_pb2.BoolCollection
    ) -> Collection[bool]:
        """Convert the protobuf message to a Python collection of bools."""
        return list(protobuf_value.values)


class BytesCollectionConverter(
    Converter[Collection[bytes], python_panel_types_pb2.ByteStringCollection]
):
    """A converter for a Collection of byte strings."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{Collection.__name__}.{bytes.__name__}"

    @property
    def protobuf_message(self) -> Type[python_panel_types_pb2.ByteStringCollection]:
        """The type-specific protobuf message for the Python type."""
        return python_panel_types_pb2.ByteStringCollection

    def to_protobuf_message(
        self, python_value: Collection[bytes]
    ) -> python_panel_types_pb2.ByteStringCollection:
        """Convert the collection of byte strings to python_panel_types_pb2.ByteStringCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(
        self, protobuf_value: python_panel_types_pb2.ByteStringCollection
    ) -> Collection[bytes]:
        """Convert the protobuf message to a Python collection of byte strings."""
        return list(protobuf_value.values)


class FloatCollectionConverter(
    Converter[Collection[float], python_panel_types_pb2.FloatCollection]
):
    """A converter for a Collection of floats."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return f"{Collection.__name__}.{float.__name__}"

    @property
    def protobuf_message(self) -> Type[python_panel_types_pb2.FloatCollection]:
        """The type-specific protobuf message for the Python type."""
        return python_panel_types_pb2.FloatCollection

    def to_protobuf_message(
        self, python_value: Collection[float]
    ) -> python_panel_types_pb2.FloatCollection:
        """Convert the collection of floats to python_panel_types_pb2.FloatCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(
        self, protobuf_value: python_panel_types_pb2.FloatCollection
    ) -> Collection[float]:
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

    def to_protobuf_message(
        self, python_value: Collection[int]
    ) -> python_panel_types_pb2.IntCollection:
        """Convert the collection of integers to python_panel_types_pb2.IntCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(
        self, protobuf_value: python_panel_types_pb2.IntCollection
    ) -> Collection[int]:
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

    def to_protobuf_message(
        self, python_value: Collection[str]
    ) -> python_panel_types_pb2.StringCollection:
        """Convert the collection of strings to python_panel_types_pb2.StringCollection."""
        return self.protobuf_message(values=python_value)

    def to_python_value(
        self, protobuf_value: python_panel_types_pb2.StringCollection
    ) -> Collection[str]:
        """Convert the protobuf message to a Python collection of strings."""
        return list(protobuf_value.values)
