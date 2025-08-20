import datetime as dt
from collections.abc import MutableMapping
from typing import Any, Union

import nitypes.bintime as bt
import numpy as np
from ni.protobuf.types import (
    precision_timestamp_conversion,
    precision_timestamp_pb2,
    waveform_pb2,
)
from nitypes.complex import ComplexInt32DType
from nitypes.waveform import (
    AnalogWaveform,
    ComplexWaveform,
    DigitalWaveform,
    NumericWaveform,
    SampleIntervalMode,
    Spectrum,
    Timing,
)

from nipanel.converters.protobuf_types import (
    DigitalWaveformConverter,
    DoubleAnalogWaveformConverter,
    DoubleComplexWaveformConverter,
    DoubleSpectrumConverter,
    Int16AnalogWaveformConverter,
    Int16ComplexWaveformConverter,
)

EXPECTED_SAMPLE_INTERVAL = 0.1
EXPECTED_T0_DT = dt.datetime(2000, 12, 1, tzinfo=dt.timezone.utc)
EXPECTED_T0_BT = bt.DateTime(EXPECTED_T0_DT)
EXPECTED_UNITS = "Volts"
EXPECTED_CHANNEL_NAME = "Dev1/ch0"
EXPECTED_ATTRIBUTES = {
    "NI_ChannelName": waveform_pb2.WaveformAttributeValue(string_value=EXPECTED_CHANNEL_NAME),
    "NI_UnitDescription": waveform_pb2.WaveformAttributeValue(string_value=EXPECTED_UNITS),
}


# ========================================================
# AnalogWaveform to protobuf
# ========================================================
def test___double_analog_waveform___convert___valid_protobuf() -> None:
    analog_waveform = AnalogWaveform.from_array_1d(np.array([1.0, 2.0, 3.0]), dtype=np.float64)
    _set_python_attributes(analog_waveform)
    _set_python_timing(analog_waveform)

    converter = DoubleAnalogWaveformConverter()
    analog_waveform_proto = converter.to_protobuf_message(analog_waveform)

    assert list(analog_waveform_proto.y_data) == [1.0, 2.0, 3.0]
    assert analog_waveform_proto.dt == EXPECTED_SAMPLE_INTERVAL
    assert analog_waveform_proto.t0 == _get_t0_pt()
    _check_protobuf_attributes(analog_waveform_proto.attributes)


def test___int16_analog_waveform___convert___valid_protobuf() -> None:
    analog_waveform = AnalogWaveform.from_array_1d(np.array([1, 2, 3]), dtype=np.int16)
    _set_python_attributes(analog_waveform)
    _set_python_timing(analog_waveform)

    converter = Int16AnalogWaveformConverter()
    analog_waveform_proto = converter.to_protobuf_message(analog_waveform)

    assert list(analog_waveform_proto.y_data) == [1, 2, 3]
    assert analog_waveform_proto.dt == EXPECTED_SAMPLE_INTERVAL
    assert analog_waveform_proto.t0 == _get_t0_pt()
    _check_protobuf_attributes(analog_waveform_proto.attributes)


# ========================================================
# AnalogWaveform from protobuf
# ========================================================
def test___double_analog_waveform___convert___valid_python_object() -> None:
    analog_waveform_proto = waveform_pb2.DoubleAnalogWaveform(
        t0=_get_t0_pt(),
        dt=EXPECTED_SAMPLE_INTERVAL,
        y_data=[1.0, 2.0, 3.0],
        attributes=EXPECTED_ATTRIBUTES,
    )

    converter = DoubleAnalogWaveformConverter()
    analog_waveform = converter.to_python_value(analog_waveform_proto)

    assert list(analog_waveform.scaled_data) == [1.0, 2.0, 3.0]
    _check_python_timing(analog_waveform)
    _check_python_attributes(analog_waveform)


def test___int16_analog_wfm___convert___valid_python_object() -> None:
    analog_waveform_proto = waveform_pb2.I16AnalogWaveform(
        t0=_get_t0_pt(),
        dt=EXPECTED_SAMPLE_INTERVAL,
        y_data=[1, 2, 3],
        attributes=EXPECTED_ATTRIBUTES,
    )

    converter = Int16AnalogWaveformConverter()
    analog_waveform = converter.to_python_value(analog_waveform_proto)

    assert list(analog_waveform.scaled_data) == [1, 2, 3]
    _check_python_timing(analog_waveform)
    _check_python_attributes(analog_waveform)


# ========================================================
# ComplexWaveform to protobuf
# ========================================================
def test___double_complex_waveform___convert___valid_protobuf() -> None:
    complex_waveform = ComplexWaveform.from_array_1d([1.5 + 2.5j, 3.5 + 4.5j], np.complex128)
    _set_python_attributes(complex_waveform)
    _set_python_timing(complex_waveform)

    converter = DoubleComplexWaveformConverter()
    complex_waveform_proto = converter.to_protobuf_message(complex_waveform)

    assert list(complex_waveform_proto.y_data) == [1.5, 2.5, 3.5, 4.5]
    assert complex_waveform_proto.dt == EXPECTED_SAMPLE_INTERVAL
    assert complex_waveform_proto.t0 == _get_t0_pt()
    _check_protobuf_attributes(complex_waveform_proto.attributes)


def test___int16_complex_waveform___convert___valid_protobuf() -> None:
    complex_waveform = ComplexWaveform.from_array_1d([(1, 2), (3, 4)], ComplexInt32DType)
    _set_python_attributes(complex_waveform)
    _set_python_timing(complex_waveform)

    converter = Int16ComplexWaveformConverter()
    complex_waveform_proto = converter.to_protobuf_message(complex_waveform)

    assert list(complex_waveform_proto.y_data) == [1, 2, 3, 4]
    assert complex_waveform_proto.dt == EXPECTED_SAMPLE_INTERVAL
    assert complex_waveform_proto.t0 == _get_t0_pt()
    _check_protobuf_attributes(complex_waveform_proto.attributes)


# ========================================================
# ComplexWaveform from protobuf
# ========================================================
def test___double_complex_waveform___convert___valid_python_object() -> None:
    complex_waveform_proto = waveform_pb2.DoubleComplexWaveform(
        t0=_get_t0_pt(),
        dt=EXPECTED_SAMPLE_INTERVAL,
        y_data=[1.0, 2.0, 3.0, 4.0],
        attributes=EXPECTED_ATTRIBUTES,
    )

    converter = DoubleComplexWaveformConverter()
    complex_waveform = converter.to_python_value(complex_waveform_proto)

    assert list(complex_waveform.scaled_data) == [1.0 + 2.0j, 3.0 + 4.0j]
    _check_python_timing(complex_waveform)
    _check_python_attributes(complex_waveform)


def test___int16_complex_wfm___convert___valid_python_object() -> None:
    complex_waveform_proto = waveform_pb2.I16ComplexWaveform(
        t0=_get_t0_pt(),
        dt=EXPECTED_SAMPLE_INTERVAL,
        y_data=[1, 2, 3, 4],
        attributes=EXPECTED_ATTRIBUTES,
    )

    converter = Int16ComplexWaveformConverter()
    complex_waveform = converter.to_python_value(complex_waveform_proto)

    expected_raw_data = np.array([(1, 2), (3, 4)], ComplexInt32DType)
    assert np.array_equal(complex_waveform.raw_data, expected_raw_data)
    _check_python_timing(complex_waveform)
    _check_python_attributes(complex_waveform)


# ========================================================
# DigitalWaveform to protobuf
# ========================================================
def test___bool_digital_waveform___convert___valid_protobuf() -> None:
    data = np.array([[0, 1, 0], [1, 0, 1]], dtype=np.bool)
    digital_waveform = DigitalWaveform.from_lines(data, signal_count=3)
    _set_python_attributes(digital_waveform)
    _set_python_timing(digital_waveform)

    converter = DigitalWaveformConverter()
    digital_waveform_proto = converter.to_protobuf_message(digital_waveform)

    assert digital_waveform_proto.y_data == b"\x00\x01\x00\x01\x00\x01"
    assert digital_waveform_proto.dt == EXPECTED_SAMPLE_INTERVAL
    assert digital_waveform_proto.t0 == _get_t0_pt()
    _check_protobuf_attributes(digital_waveform_proto.attributes, check_units=False)


def test___uint8_digital_waveform___convert___valid_protobuf() -> None:
    data = np.array([[0, 1, 3], [7, 5, 1]], dtype=np.uint8)
    digital_waveform = DigitalWaveform.from_lines(data, signal_count=3)
    _set_python_attributes(digital_waveform)
    _set_python_timing(digital_waveform)

    converter = DigitalWaveformConverter()
    digital_waveform_proto = converter.to_protobuf_message(digital_waveform)

    assert digital_waveform_proto.y_data == b"\x00\x01\x03\x07\x05\x01"
    assert digital_waveform_proto.dt == EXPECTED_SAMPLE_INTERVAL
    assert digital_waveform_proto.t0 == _get_t0_pt()
    _check_protobuf_attributes(digital_waveform_proto.attributes, check_units=False)


# ========================================================
# DigitalWaveform from protobuf
# ========================================================
def test___bool_digital_waveform___convert___valid_python_object() -> None:
    data = np.array([[0, 1, 0], [1, 0, 1]], dtype=np.bool)
    digital_waveform_proto = waveform_pb2.DigitalWaveform(
        t0=_get_t0_pt(),
        dt=EXPECTED_SAMPLE_INTERVAL,
        signal_count=3,
        y_data=data.tobytes(),
        attributes=EXPECTED_ATTRIBUTES,
    )

    converter = DigitalWaveformConverter()
    digital_waveform = converter.to_python_value(digital_waveform_proto)

    assert np.array_equal(digital_waveform.data, data)
    _check_python_timing(digital_waveform)
    _check_python_attributes(digital_waveform)


def test___uint8_digital_waveform___convert___valid_python_object() -> None:
    data = np.array([[0, 1], [2, 3], [4, 5], [6, 7]], dtype=np.uint8)
    digital_waveform_proto = waveform_pb2.DigitalWaveform(
        t0=_get_t0_pt(),
        dt=EXPECTED_SAMPLE_INTERVAL,
        signal_count=2,
        y_data=data.tobytes(),
        attributes=EXPECTED_ATTRIBUTES,
    )

    converter = DigitalWaveformConverter()
    digital_waveform = converter.to_python_value(digital_waveform_proto)

    assert np.array_equal(digital_waveform.data, data)
    _check_python_timing(digital_waveform)
    _check_python_attributes(digital_waveform)


# ========================================================
# Spectrum to protobuf
# ========================================================
def test___float64_spectrum___convert___valid_protobuf() -> None:
    spectrum = Spectrum.from_array_1d(np.array([1.0, 2.0, 3.0]))
    spectrum.start_frequency = 100.0
    spectrum.frequency_increment = 10.0
    _set_python_attributes(spectrum)

    converter = DoubleSpectrumConverter()
    spectrum_proto = converter.to_protobuf_message(spectrum)

    assert list(spectrum_proto.data) == [1.0, 2.0, 3.0]
    assert spectrum_proto.start_frequency == 100.0
    assert spectrum_proto.frequency_increment == 10.0
    _check_protobuf_attributes(spectrum_proto.attributes)


# ========================================================
# Spectrum from protobuf
# ========================================================
def test___double_spectrum___convert___valid_python_object() -> None:
    spectrum_proto = waveform_pb2.DoubleSpectrum(
        data=[1.0, 2.0, 3.0],
        start_frequency=100.0,
        frequency_increment=10.0,
        attributes=EXPECTED_ATTRIBUTES,
    )

    converter = DoubleSpectrumConverter()
    spectrum = converter.to_python_value(spectrum_proto)

    assert list(spectrum.data) == [1.0, 2.0, 3.0]
    assert spectrum.start_frequency == 100.0
    assert spectrum.frequency_increment == 10.0
    _check_python_attributes(spectrum)


# ========================================================
# Helpers
# ========================================================
def _get_t0_pt() -> precision_timestamp_pb2.PrecisionTimestamp:
    return precision_timestamp_conversion.bintime_datetime_to_protobuf(EXPECTED_T0_BT)


def _set_python_attributes(
    waveform: Union[NumericWaveform[Any, Any], DigitalWaveform[Any], Spectrum[Any]],
) -> None:
    waveform.channel_name = EXPECTED_CHANNEL_NAME
    if isinstance(waveform, NumericWaveform) or isinstance(waveform, Spectrum):
        waveform.unit_description = EXPECTED_UNITS


def _check_python_attributes(
    waveform: Union[NumericWaveform[Any, Any], DigitalWaveform[Any], Spectrum[Any]],
) -> None:
    assert waveform.channel_name == EXPECTED_CHANNEL_NAME
    if isinstance(waveform, NumericWaveform) or isinstance(waveform, Spectrum):
        assert waveform.unit_description == EXPECTED_UNITS


def _check_protobuf_attributes(
    attributes: MutableMapping[str, waveform_pb2.WaveformAttributeValue],
    check_units: bool = True,
) -> None:
    assert attributes["NI_ChannelName"].string_value == EXPECTED_CHANNEL_NAME
    if check_units:
        assert attributes["NI_UnitDescription"].string_value == EXPECTED_UNITS


def _set_python_timing(waveform: Union[NumericWaveform[Any, Any], DigitalWaveform[Any]]) -> None:
    waveform.timing = Timing.create_with_regular_interval(
        sample_interval=dt.timedelta(milliseconds=EXPECTED_SAMPLE_INTERVAL * 1000),
        timestamp=EXPECTED_T0_DT,
    )


def _check_python_timing(waveform: Union[NumericWaveform[Any, Any], DigitalWaveform[Any]]) -> None:
    assert waveform.timing.start_time == EXPECTED_T0_DT
    assert waveform.timing.sample_interval == dt.timedelta(seconds=EXPECTED_SAMPLE_INTERVAL)
    assert waveform.timing.sample_interval_mode == SampleIntervalMode.REGULAR
