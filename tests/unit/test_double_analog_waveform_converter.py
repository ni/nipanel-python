import datetime as dt

import numpy
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.precision_timestamp_pb2 import (
    PrecisionTimestamp,
)
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.waveform_pb2 import (
    DoubleAnalogWaveform,
    WaveformAttributeValue,
)
from nitypes.bintime import DateTime
from nitypes.waveform import AnalogWaveform, NoneScaleMode, Timing

from nipanel.converters.double_analog_waveform import (
    DoubleAnalogWaveformConverter,
    PrecisionTimestampConverter,
)


#########################################################
# Python --> Protobuf
#########################################################
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
    t0_dt = dt.datetime(2000, 12, 1, tzinfo=dt.timezone.utc)
    analog_waveform.timing = Timing.create_with_regular_interval(
        sample_interval=dt.timedelta(milliseconds=1000),
        timestamp=t0_dt,
    )

    converter = DoubleAnalogWaveformConverter()
    dbl_analog_waveform = converter.to_protobuf_message(analog_waveform)

    assert dbl_analog_waveform.dt == 1.0

    bin_dt = DateTime(t0_dt)
    pt_converter = PrecisionTimestampConverter()
    converted_t0 = pt_converter.to_protobuf_message(bin_dt)
    assert dbl_analog_waveform.t0 == converted_t0


#########################################################
# Protobuf --> Python
#########################################################
def test___default_dbl_analog_wfm___convert___valid_python_object() -> None:
    dbl_analog_wfm = DoubleAnalogWaveform()
    converter = DoubleAnalogWaveformConverter()
    analog_waveform = converter.to_python_value(dbl_analog_wfm)

    assert not analog_waveform.extended_properties
    assert analog_waveform.timing.sample_interval == dt.timedelta()
    assert analog_waveform.timing.start_time == dt.datetime(1904, 1, 1, tzinfo=dt.timezone.utc)
    assert analog_waveform.scaled_data.size == 0
    assert analog_waveform.scale_mode == NoneScaleMode()


def test___dbl_analog_wfm_with_y_data___convert___valid_python_object() -> None:
    dbl_analog_wfm = DoubleAnalogWaveform(y_data=[1.0, 2.0, 3.0])
    converter = DoubleAnalogWaveformConverter()
    analog_waveform = converter.to_python_value(dbl_analog_wfm)

    assert list(analog_waveform.scaled_data) == [1.0, 2.0, 3.0]


def test___dbl_analog_wfm_with_attributes___convert___valid_python_object() -> None:
    attributes = {
        "NI_ChannelName": WaveformAttributeValue(string_value="Dev1/ai0"),
        "NI_UnitDescription": WaveformAttributeValue(string_value="Volts"),
    }
    dbl_analog_wfm = DoubleAnalogWaveform(attributes=attributes)
    converter = DoubleAnalogWaveformConverter()
    analog_waveform = converter.to_python_value(dbl_analog_wfm)

    assert analog_waveform.channel_name == "Dev1/ai0"
    assert analog_waveform.unit_description == "Volts"


def test___dbl_analog_wfm_with_timing___convert___valid_python_object() -> None:
    t0_dt = DateTime(2020, 5, 5, tzinfo=dt.timezone.utc)
    pt_converter = PrecisionTimestampConverter()
    t0_pt = pt_converter.to_protobuf_message(t0_dt)
    dbl_analog_wfm = DoubleAnalogWaveform(t0=t0_pt, dt=0.1, y_data=[1.0, 2.0, 3.0])
    converter = DoubleAnalogWaveformConverter()
    analog_waveform = converter.to_python_value(dbl_analog_wfm)

    assert analog_waveform.timing.start_time == t0_dt._to_datetime_datetime()
    assert analog_waveform.timing.sample_interval == dt.timedelta(seconds=0.1)
