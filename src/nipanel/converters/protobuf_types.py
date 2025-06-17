"""Classes to convert between measurement specific protobuf types and containers."""

import collections.abc
from typing import Type, Union

import hightime as ht
import numpy
from ni.protobuf.types import scalar_pb2
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.precision_timestamp_pb2 import (
    PrecisionTimestamp,
)
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.waveform_pb2 import (
    DoubleAnalogWaveform,
    WaveformAttributeValue,
)
from nitypes.bintime import DateTime, TimeValueTuple
from nitypes.scalar import Scalar
from nitypes.waveform import (
    AnalogWaveform,
    ExtendedPropertyDictionary,
    NoneScaleMode,
    SampleIntervalMode,
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
        """Convert the Python AnalogWaveform to a protobuf DoubleAnalogWaveform."""
        if python_value.timing.has_timestamp:
            pt_converter = PrecisionTimestampConverter()
            bin_datetime = DateTime(python_value.timing.start_time)
            precision_timestamp = pt_converter.to_protobuf_message(bin_datetime)
        else:
            precision_timestamp = PrecisionTimestamp(seconds=0, fractional_seconds=0)

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
        attributes = {}
        for key, value in extended_properties.items():
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

        return attributes

    def to_python_value(
        self, protobuf_value: DoubleAnalogWaveform
    ) -> AnalogWaveform[numpy.float64]:
        """Convert the protobuf DoubleAnalogWaveform to a Python AnalogWaveform."""
        if (
            not protobuf_value.dt
            and not protobuf_value.t0.seconds
            and not protobuf_value.t0.fractional_seconds
        ):
            # If both dt and t0 and unset, use Timing.empty.
            timing = Timing.empty
        else:
            # Timestamp
            pt_converter = PrecisionTimestampConverter()
            bin_datetime = pt_converter.to_python_value(protobuf_value.t0)
            timestamp = bin_datetime._to_datetime_datetime()

            # Sample Interval
            if not protobuf_value.dt:
                sample_interval_mode = SampleIntervalMode.NONE
                sample_interval = None
            else:
                sample_interval_mode = SampleIntervalMode.REGULAR
                sample_interval = ht.timedelta(seconds=protobuf_value.dt)

            timing = Timing(
                sample_interval_mode=sample_interval_mode,
                timestamp=timestamp,
                sample_interval=sample_interval,
            )

        extended_properties = {}
        for key, value in protobuf_value.attributes.items():
            attr_type = value.WhichOneof("attribute")
            extended_properties[key] = getattr(value, str(attr_type))

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
        seconds, fractional_seconds = python_value.to_tuple()
        return self.protobuf_message(seconds=seconds, fractional_seconds=fractional_seconds)

    def to_python_value(self, protobuf_value: PrecisionTimestamp) -> DateTime:
        """Convert the protobuf PrecisionTimestamp to a Python DateTime."""
        time_value_tuple = TimeValueTuple(protobuf_value.seconds, protobuf_value.fractional_seconds)
        return DateTime.from_tuple(time_value_tuple)


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

    def to_python_value(self, protobuf_value: scalar_pb2.ScalarData) -> Scalar[_AnyScalarType]:
        """Convert the protobuf message to a Python Scalar."""
        if protobuf_value.units is None:
            raise ValueError("protobuf.units cannot be None.")

        pb_type = str(protobuf_value.WhichOneof("value"))
        if pb_type not in _SCALAR_TYPE_TO_PB_ATTR_MAP.values():
            raise ValueError(f"Unexpected value for protobuf_value.WhichOneOf: {pb_type}")

        value = getattr(protobuf_value, pb_type)
        return Scalar(value, protobuf_value.units)
