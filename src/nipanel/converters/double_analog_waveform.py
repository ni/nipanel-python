"""Classes to convert between builtin Python scalars and containers."""

import datetime as dt
from typing import Type

import numpy
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.precision_timestamp_pb2 import (
    PrecisionTimestamp,
)
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.waveform_pb2 import (
    DoubleAnalogWaveform,
    WaveformAttributeValue,
)
from nitypes.bintime import DateTime, TimeDelta
from nitypes.waveform import AnalogWaveform, NoneScaleMode, Timing

from nipanel.converters import Converter


class DoubleAnalogWaveformConverter(Converter[AnalogWaveform[numpy.float64], DoubleAnalogWaveform]):
    """A converter for AnalogWaveform types with scaled data (double)."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return AnalogWaveform.__name__

    @property
    def protobuf_message(self) -> Type[DoubleAnalogWaveform]:
        """The type-specific protobuf message for the Python type."""
        return DoubleAnalogWaveform

    def to_protobuf_message(
        self, python_value: AnalogWaveform[numpy.float64]
    ) -> DoubleAnalogWaveform:
        """Convert the Python bool to a protobuf wrappers_pb2.BoolValue."""
        attributes = {}
        for key, value in python_value.extended_properties.items():
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

        if python_value.timing != Timing.empty:
            pt_converter = PrecisionTimestampConverter()
            bin_datetime = DateTime(python_value.timing.start_time)
            precision_timestamp = pt_converter.to_protobuf_message(bin_datetime)
            time_interval = python_value.timing.sample_interval.total_seconds()
        else:
            precision_timestamp = PrecisionTimestamp(seconds=0, fractional_seconds=0)
            time_interval = 0

        return self.protobuf_message(
            t0=precision_timestamp,
            dt=time_interval,
            y_data=python_value.scaled_data,
            attributes=attributes,
        )

    def to_python_value(
        self, protobuf_value: DoubleAnalogWaveform
    ) -> AnalogWaveform[numpy.float64]:
        """Convert the protobuf message to a Python bool."""
        extended_properties = {}
        for key, value in protobuf_value.attributes.items():
            attr_type = value.WhichOneof("attribute")
            extended_properties[key] = getattr(value, str(attr_type))

        pt_converter = PrecisionTimestampConverter()
        bin_datetime = pt_converter.to_python_value(protobuf_value.t0)
        timestamp = bin_datetime._to_datetime_datetime()
        print(f"-- {timestamp}")
        sample_interval = dt.timedelta(seconds=protobuf_value.dt)
        timing = Timing.create_with_regular_interval(
            sample_interval,
            timestamp,
        )

        data_list = list(protobuf_value.y_data)
        return AnalogWaveform(
            sample_count=len(data_list),
            dtype=numpy.float64,
            raw_data=numpy.array(data_list),
            start_index=0,
            capacity=len(data_list),
            extended_properties=extended_properties,
            copy_extended_properties=True,
            timing=timing,
            scale_mode=NoneScaleMode(),
        )


class PrecisionTimestampConverter(Converter[DateTime, PrecisionTimestamp]):
    """A converter for bintime.DateTime types."""

    @property
    def python_typename(self) -> str:
        """The Python type that this converter handles."""
        return DateTime.__name__

    @property
    def protobuf_message(self) -> Type[PrecisionTimestamp]:
        """The type-specific protobuf message for the Python type."""
        return PrecisionTimestamp

    def to_protobuf_message(self, python_value: DateTime) -> PrecisionTimestamp:
        """Convert the Python DateTime to a protobuf PrecisionTimestamp."""
        time_delta: TimeDelta = DateTime._to_offset(python_value._to_datetime_datetime())
        ticks = TimeDelta._to_ticks(time_delta.total_seconds())
        seconds = ticks >> 64
        frac_seconds = ticks & ((1 << 64) - 1)
        return self.protobuf_message(seconds=seconds, fractional_seconds=frac_seconds)

    def to_python_value(self, protobuf_value: PrecisionTimestamp) -> DateTime:
        """Convert the protobuf message to a Python DateTime."""
        ticks = (protobuf_value.seconds << 64) | protobuf_value.fractional_seconds
        print(f"ticks: {ticks}")
        return DateTime.from_ticks(ticks)
