from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.waveform_pb2 import DoubleAnalogWaveform, WaveformAttributeValue
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.precision_timestamp_pb2 import PrecisionTimestamp
from nitypes.waveform import AnalogWaveform
from nitypes.bintime import TimeDelta, DateTime
from nitypes.waveform import NoneScaleMode, Timing

from nipanel.converters.double_analog_waveform import DoubleAnalogWaveformConverter

import numpy
import datetime as dt


def test___default_analog_waveform___convert___valid_protobuf() -> None:
    analog_waveform = AnalogWaveform()
    converter = DoubleAnalogWaveformConverter()
    dbl_analog_waveform = converter.to_protobuf_message(analog_waveform)

    assert not dbl_analog_waveform.attributes
    assert dbl_analog_waveform.dt == 0
    assert dbl_analog_waveform.t0 == PrecisionTimestamp(seconds=0, fractional_seconds=0)
    assert list(dbl_analog_waveform.y_data) == []


def test___analog_waveform_samples_only___convert___valid_protobuf() -> None:
    analog_waveform = AnalogWaveform(5)
    
    converter = DoubleAnalogWaveformConverter()
    dbl_analog_waveform = converter.to_protobuf_message(analog_waveform)

    assert list(dbl_analog_waveform.y_data) == [0.0, 0.0, 0.0, 0.0, 0.0]


def test___analog_waveform_non_zero_samples___convert___valid_protobuf() -> None:
    analog_waveform = AnalogWaveform.from_array_1d(numpy.array([1.0, 2.0, 3.0]))
    
    converter = DoubleAnalogWaveformConverter()
    dbl_analog_waveform = converter.to_protobuf_message(analog_waveform)

    assert list(dbl_analog_waveform.y_data) == [1.0, 2.0, 3.0]


def test___analog_waveform_with_extended_properties___convert___valid_protobuf() -> None:
    analog_waveform = AnalogWaveform()
    analog_waveform.channel_name = "Dev1/ai0"
    analog_waveform.unit_description = "Volts"

    converter = DoubleAnalogWaveformConverter()
    dbl_analog_waveform = converter.to_protobuf_message(analog_waveform)

    assert dbl_analog_waveform.attributes["NI_ChannelName"].string_value == "Dev1/ai0"
    assert dbl_analog_waveform.attributes["NI_UnitDescription"].string_value == "Volts"


def test___analog_waveform_with_standard_timing___convert___valid_protobuf() -> None:
    analog_waveform = AnalogWaveform.from_array_1d(numpy.array([1.0, 2.0, 3.0]))
    analog_waveform.timing = Timing.create_with_regular_interval(
        sample_interval=dt.timedelta(milliseconds=1),
        timestamp=dt.datetime(2000, 12, 1, tzinfo=dt.timezone.utc),
    )
    
    converter = DoubleAnalogWaveformConverter()
    dbl_analog_waveform = converter.to_protobuf_message(analog_waveform)

    assert dbl_analog_waveform.dt == 1.0
