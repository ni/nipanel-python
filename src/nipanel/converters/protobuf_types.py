"""Classes to convert between measurement specific protobuf types and containers."""

import collections.abc
from typing import Type, Union

import hightime as ht
import nitypes.bintime as bt
import numpy as np
from ni.protobuf.types import scalar_pb2
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.precision_timestamp_pb2 import (
    PrecisionTimestamp,
)
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.waveform_pb2 import (
    DoubleAnalogWaveform,
    WaveformAttributeValue,
)
from nitypes.scalar import Scalar
from nitypes.time import convert_datetime
from nitypes.waveform import (
    AnalogWaveform,
    ExtendedPropertyDictionary,
    ExtendedPropertyValue,
    NoneScaleMode,
    Timing,
)
from typing_extensions import TypeAlias

from nipanel.converters import Converter

_AnyScalarType: TypeAlias = Union[bool, int, float, str]
_SCALAR_TYPE_TO_PB_ATTR_MAP = {
    bool: "bool_value",
    int: "int32_value",
    float: "double_value",
    str: "string_value",
}


class DoubleAnalogWaveformConverter(Converter[AnalogWaveform[np.float64], DoubleAnalogWaveform]):
    """A converter for AnalogWaveform types with scaled data (double)."""

    def __init__(self) -> None:
        """Initialize a DoubleAnalogWaveformConverter object."""
        self._pt_converter = PrecisionTimestampConverter()

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return AnalogWaveform.__name__

    @property
    def protobuf_message(self) -> Type[DoubleAnalogWaveform]:
        """The type-specific protobuf message for the Python type."""
        return DoubleAnalogWaveform

    def to_protobuf_message(self, python_value: AnalogWaveform[np.float64]) -> DoubleAnalogWaveform:
        """Convert the Python AnalogWaveform to a protobuf DoubleAnalogWaveform."""
        if python_value.timing.has_timestamp:
            bin_datetime = convert_datetime(bt.DateTime, python_value.timing.start_time)
            precision_timestamp = self._pt_converter.to_protobuf_message(bin_datetime)
        else:
            precision_timestamp = None

        if python_value.timing.has_sample_interval:
            time_interval = python_value.timing.sample_interval.total_seconds()
        else:
            time_interval = 0

        attributes = self._extended_properties_to_attributes(python_value.extended_properties)

        return self.protobuf_message(
            t0=precision_timestamp,
            dt=time_interval,
            y_data=python_value.scaled_data,
            attributes=attributes,
        )

    def _extended_properties_to_attributes(
        self,
        extended_properties: ExtendedPropertyDictionary,
    ) -> collections.abc.Mapping[str, WaveformAttributeValue]:
        return {key: self._value_to_attribute(value) for key, value in extended_properties.items()}

    def _value_to_attribute(self, value: ExtendedPropertyValue) -> WaveformAttributeValue:
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

        return attr_value

    def to_python_value(self, protobuf_message: DoubleAnalogWaveform) -> AnalogWaveform[np.float64]:
        """Convert the protobuf DoubleAnalogWaveform to a Python AnalogWaveform."""
        if not protobuf_message.dt and not protobuf_message.HasField("t0"):
            # If both dt and t0 are unset, use Timing.empty.
            timing = Timing.empty
        else:
            # Timestamp
            pt_converter = PrecisionTimestampConverter()
            bin_datetime = pt_converter.to_python_value(protobuf_message.t0)
            # TODO: We shouldn't need to convert to dt.datetime here.
            # I'm only doing this to avoid a mypy error. This needs to be fixed.
            timestamp = bin_datetime._to_datetime_datetime()

            # Sample Interval
            if not protobuf_message.dt:
                timing = Timing.create_with_no_interval(timestamp=timestamp)
            else:
                sample_interval = ht.timedelta(seconds=protobuf_message.dt)
                timing = Timing.create_with_regular_interval(
                    sample_interval=sample_interval,
                    timestamp=timestamp,
                )

        extended_properties = {}
        for key, value in protobuf_message.attributes.items():
            attr_type = value.WhichOneof("attribute")
            extended_properties[key] = getattr(value, str(attr_type))

        data_array = np.array(protobuf_message.y_data)
        return AnalogWaveform(
            sample_count=data_array.size,
            dtype=np.float64,
            raw_data=data_array,
            start_index=0,
            capacity=data_array.size,
            extended_properties=extended_properties,
            copy_extended_properties=True,
            timing=timing,
            scale_mode=NoneScaleMode(),
        )


class PrecisionTimestampConverter(Converter[bt.DateTime, PrecisionTimestamp]):
    """A converter for bintime.DateTime types."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return bt.DateTime.__name__

    @property
    def protobuf_message(self) -> Type[PrecisionTimestamp]:
        """The type-specific protobuf message for the Python type."""
        return PrecisionTimestamp

    def to_protobuf_message(self, python_value: bt.DateTime) -> PrecisionTimestamp:
        """Convert the Python DateTime to a protobuf PrecisionTimestamp."""
        seconds, fractional_seconds = python_value.to_tuple()
        return self.protobuf_message(seconds=seconds, fractional_seconds=fractional_seconds)

    def to_python_value(self, protobuf_message: PrecisionTimestamp) -> bt.DateTime:
        """Convert the protobuf PrecisionTimestamp to a Python DateTime."""
        time_value_tuple = bt.TimeValueTuple(
            protobuf_message.seconds, protobuf_message.fractional_seconds
        )
        return bt.DateTime.from_tuple(time_value_tuple)


class ScalarConverter(Converter[Scalar[_AnyScalarType], scalar_pb2.ScalarData]):
    """A converter for Scalar objects."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return Scalar.__name__

    @property
    def protobuf_message(self) -> Type[scalar_pb2.ScalarData]:
        """The type-specific protobuf message for the Python type."""
        return scalar_pb2.ScalarData

    def to_protobuf_message(self, python_value: Scalar[_AnyScalarType]) -> scalar_pb2.ScalarData:
        """Convert the Python Scalar to a protobuf scalar_pb2.ScalarData."""
        message = self.protobuf_message()
        message.units = python_value.units

        value_attr = _SCALAR_TYPE_TO_PB_ATTR_MAP.get(type(python_value.value), None)
        if not value_attr:
            raise TypeError(f"Unexpected type for python_value.value: {type(python_value.value)}")
        setattr(message, value_attr, python_value.value)

        return message

    def to_python_value(self, protobuf_message: scalar_pb2.ScalarData) -> Scalar[_AnyScalarType]:
        """Convert the protobuf message to a Python Scalar."""
        if protobuf_message.units is None:
            raise ValueError("protobuf.units cannot be None.")

        pb_type = str(protobuf_message.WhichOneof("value"))
        if pb_type not in _SCALAR_TYPE_TO_PB_ATTR_MAP.values():
            raise ValueError(f"Unexpected value for protobuf_value.WhichOneOf: {pb_type}")

        value = getattr(protobuf_message, pb_type)
        return Scalar(value, protobuf_message.units)
