import datetime as dt

import numpy
import pytest
from ni.protobuf.types.scalar_pb2 import ScalarData
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.waveform_pb2 import (
    DoubleAnalogWaveform,
    WaveformAttributeValue,
)
from nitypes.bintime import DateTime
from nitypes.scalar import Scalar
from nitypes.waveform import AnalogWaveform, NoneScaleMode, SampleIntervalMode, Timing

from nipanel.converters.protobuf_types import (
    DoubleAnalogWaveformConverter,
    PrecisionTimestampConverter,
    ScalarConverter,
)


# ========================================================
# AnalogWaveform to DoubleAnalogWaveform
# ========================================================
def test___default_analog_waveform___convert___valid_protobuf() -> None:
    analog_waveform = AnalogWaveform()

    converter = DoubleAnalogWaveformConverter()
    dbl_analog_waveform = converter.to_protobuf_message(analog_waveform)

    assert not dbl_analog_waveform.attributes
    assert dbl_analog_waveform.dt == 0
    assert not dbl_analog_waveform.HasField("t0")
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


# ========================================================
# DoubleAnalogWaveform to AnalogWaveform
# ========================================================
def test___default_dbl_analog_wfm___convert___valid_python_object() -> None:
    dbl_analog_wfm = DoubleAnalogWaveform()

    converter = DoubleAnalogWaveformConverter()
    analog_waveform = converter.to_python_value(dbl_analog_wfm)

    assert not analog_waveform.extended_properties
    assert analog_waveform.timing == Timing.empty
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
    assert analog_waveform.timing.sample_interval_mode == SampleIntervalMode.REGULAR


def test___dbl_analog_wfm_with_timing_no_t0___convert___valid_python_object() -> None:
    dbl_analog_wfm = DoubleAnalogWaveform(dt=0.1, y_data=[1.0, 2.0, 3.0])

    converter = DoubleAnalogWaveformConverter()
    analog_waveform = converter.to_python_value(dbl_analog_wfm)

    assert analog_waveform.timing.start_time == dt.datetime(1904, 1, 1, tzinfo=dt.timezone.utc)
    assert analog_waveform.timing.sample_interval == dt.timedelta(seconds=0.1)
    assert analog_waveform.timing.sample_interval_mode == SampleIntervalMode.REGULAR


def test___dbl_analog_wfm_with_timing_no_dt___convert___valid_python_object() -> None:
    t0_dt = DateTime(2020, 5, 5, tzinfo=dt.timezone.utc)
    pt_converter = PrecisionTimestampConverter()
    t0_pt = pt_converter.to_protobuf_message(t0_dt)
    dbl_analog_wfm = DoubleAnalogWaveform(t0=t0_pt, y_data=[1.0, 2.0, 3.0])

    converter = DoubleAnalogWaveformConverter()
    analog_waveform = converter.to_python_value(dbl_analog_wfm)

    assert analog_waveform.timing.start_time == t0_dt._to_datetime_datetime()
    assert not analog_waveform.timing.has_sample_interval
    assert analog_waveform.timing.sample_interval_mode == SampleIntervalMode.NONE


# ========================================================
# ScalarData to Scalar
# ========================================================
def test___bool_scalar_protobuf___convert___valid_bool_scalar() -> None:
    protobuf_value = ScalarData()
    protobuf_value.units = "volts"
    protobuf_value.bool_value = True

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, bool)
    assert python_value.value is True
    assert python_value.units == "volts"


def test___int32_scalar_protobuf___convert___valid_int_scalar() -> None:
    protobuf_value = ScalarData()
    protobuf_value.units = "volts"
    protobuf_value.int32_value = 10

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, int)
    assert python_value.value == 10
    assert python_value.units == "volts"


def test___double_scalar_protobuf___convert___valid_float_scalar() -> None:
    protobuf_value = ScalarData()
    protobuf_value.units = "volts"
    protobuf_value.double_value = 20.0

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, float)
    assert python_value.value == 20.0
    assert python_value.units == "volts"


def test___string_scalar_protobuf___convert___valid_str_scalar() -> None:
    protobuf_value = ScalarData()
    protobuf_value.units = "volts"
    protobuf_value.string_value = "value"

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, str)
    assert python_value.value == "value"
    assert python_value.units == "volts"


def test___scalar_protobuf_value_unset___convert___throws_type_error() -> None:
    protobuf_value = ScalarData()
    protobuf_value.units = "volts"

    converter = ScalarConverter()
    with pytest.raises(ValueError) as exc:
        _ = converter.to_python_value(protobuf_value)

    assert exc.value.args[0].startswith("Unexpected value for protobuf_value.WhichOneOf")


def test___scalar_protobuf_units_unset___convert___python_units_blank() -> None:
    protobuf_value = ScalarData()
    protobuf_value.bool_value = True

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, bool)
    assert python_value.value is True
    assert python_value.units == ""


# ========================================================
# Scalar to ScalarData
# ========================================================
def test___bool_scalar___convert___valid_bool_scalar_protobuf() -> None:
    python_value = Scalar(True, "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "bool_value"
    assert protobuf_value.bool_value is True
    assert protobuf_value.units == "volts"


def test___int_scalar___convert___valid_int32_scalar_protobuf() -> None:
    python_value = Scalar(10, "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "int32_value"
    assert protobuf_value.int32_value == 10
    assert protobuf_value.units == "volts"


def test___float_scalar___convert___valid_double_scalar_protobuf() -> None:
    python_value = Scalar(20.0, "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "double_value"
    assert protobuf_value.double_value == 20.0
    assert protobuf_value.units == "volts"


def test___str_scalar___convert___valid_string_scalar_protobuf() -> None:
    python_value = Scalar("value", "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "string_value"
    assert protobuf_value.string_value == "value"
    assert protobuf_value.units == "volts"


def test___scalar_units_unset___convert___protobuf_units_blank() -> None:
    python_value = Scalar(10)

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "int32_value"
    assert protobuf_value.int32_value == 10
    assert protobuf_value.units == ""
