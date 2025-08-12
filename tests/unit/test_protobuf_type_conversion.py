import datetime as dt
from typing_extensions import Mapping

import numpy
import pytest
from ni.protobuf.types import attribute_value_pb2, scalar_pb2
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.array_pb2 import (
    Double2DArray,
)
from ni.protobuf.types.waveform_pb2 import (
    DoubleAnalogWaveform,
    WaveformAttributeValue,
)
from nitypes.bintime import DateTime
from nitypes.scalar import Scalar
from nitypes.waveform import AnalogWaveform, NoneScaleMode, SampleIntervalMode, Timing

from nipanel.converters.protobuf_types import (
    Double2DArrayConverter,
    DoubleAnalogWaveformConverter,
    PrecisionTimestampConverter,
    ScalarConverter,
)


# ========================================================
# list[list[float]] to Double2DArray
# Other collection types are tested in test_convert.py
# ========================================================
@pytest.mark.parametrize(
    "list_of_lists, expected_data, expected_rows, expected_columns",
    [
        ([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], [1.0, 2.0, 3.0, 4.0, 5.0, 6.0], 3, 2),
        ([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], [1.0, 2.0, 3.0, 4.0, 5.0, 6.0], 2, 3),
    ],
)
def test___list_of_lists___convert___valid_double2darray(
    list_of_lists: list[list[float]],
    expected_data: list[float],
    expected_rows: int,
    expected_columns: int,
) -> None:
    converter = Double2DArrayConverter()
    result = converter.to_protobuf_message(list_of_lists)

    assert result.data == expected_data
    assert result.rows == expected_rows
    assert result.columns == expected_columns


def test___list_of_lists_inconsistent_column_length___convert___throws_value_error() -> None:
    converter = Double2DArrayConverter()

    with pytest.raises(ValueError):
        _ = converter.to_protobuf_message([[1.0, 2.0], [3.0, 4.0, 5.0]])


# ========================================================
# Double2DArray to list[list[float]]
# Other collection types are tested in test_convert.py
# ========================================================
@pytest.mark.parametrize(
    "double2darray, expected_data",
    [
        (
            Double2DArray(rows=3, columns=2, data=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]),
            [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
        ),
        (
            Double2DArray(rows=2, columns=3, data=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]),
            [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
        ),
    ],
)
def test___double2darray___convert___valid_list_of_lists(
    double2darray: Double2DArray, expected_data: list[list[float]]
) -> None:
    converter = Double2DArrayConverter()
    list_of_lists = converter.to_python_value(double2darray)

    assert list_of_lists == expected_data


def test___double2darray_invalid_num_columns___convert___throws_value_error() -> None:
    double2darray = Double2DArray(rows=1, columns=2, data=[1.0, 2.0, 3.0])
    converter = Double2DArrayConverter()

    with pytest.raises(ValueError):
        _ = converter.to_python_value(double2darray)


def test___double2darray_empty_data___convert___returns_empty_list() -> None:
    double2darray = Double2DArray(rows=0, columns=0, data=[])
    converter = Double2DArrayConverter()

    list_of_lists = converter.to_python_value(double2darray)

    assert not list_of_lists


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
# Scalar: Protobuf to Python
# ========================================================
def test___bool_scalar_protobuf___convert___valid_bool_scalar() -> None:
    attrs = _units_to_scalar_attribute_map("volts")
    protobuf_value = scalar_pb2.Scalar(attributes=attrs)
    protobuf_value.bool_value = True

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, bool)
    assert python_value.value is True
    assert python_value.units == "volts"


def test___int32_scalar_protobuf___convert___valid_int_scalar() -> None:
    attrs = _units_to_scalar_attribute_map("volts")
    protobuf_value = scalar_pb2.Scalar(attributes=attrs)
    protobuf_value.sint32_value = 10

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, int)
    assert python_value.value == 10
    assert python_value.units == "volts"


def test___double_scalar_protobuf___convert___valid_float_scalar() -> None:
    attrs = _units_to_scalar_attribute_map("volts")
    protobuf_value = scalar_pb2.Scalar(attributes=attrs)
    protobuf_value.double_value = 20.0

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, float)
    assert python_value.value == 20.0
    assert python_value.units == "volts"


def test___string_scalar_protobuf___convert___valid_str_scalar() -> None:
    attrs = _units_to_scalar_attribute_map("volts")
    protobuf_value = scalar_pb2.Scalar(attributes=attrs)
    protobuf_value.string_value = "value"

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, str)
    assert python_value.value == "value"
    assert python_value.units == "volts"


def test___scalar_protobuf_value_unset___convert___throws_type_error() -> None:
    attrs = _units_to_scalar_attribute_map("volts")
    protobuf_value = scalar_pb2.Scalar(attributes=attrs)

    converter = ScalarConverter()
    with pytest.raises(ValueError) as exc:
        _ = converter.to_python_value(protobuf_value)

    assert exc.value.args[0].startswith("Unexpected value for protobuf_value.WhichOneOf")


def test___scalar_protobuf_units_unset___convert___python_units_blank() -> None:
    protobuf_value = scalar_pb2.Scalar()
    protobuf_value.bool_value = True

    converter = ScalarConverter()
    python_value = converter.to_python_value(protobuf_value)

    assert isinstance(python_value.value, bool)
    assert python_value.value is True
    assert python_value.units == ""


# ========================================================
# Scalar: Python to Protobuf
# ========================================================
def test___bool_scalar___convert___valid_bool_scalar_protobuf() -> None:
    python_value = Scalar(True, "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "bool_value"
    assert protobuf_value.bool_value is True
    assert protobuf_value.attributes["NI_UnitDescription"].string_value == "volts"


def test___int_scalar___convert___valid_int32_scalar_protobuf() -> None:
    python_value = Scalar(10, "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "sint32_value"
    assert protobuf_value.sint32_value == 10
    assert protobuf_value.attributes["NI_UnitDescription"].string_value == "volts"


def test___float_scalar___convert___valid_double_scalar_protobuf() -> None:
    python_value = Scalar(20.0, "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "double_value"
    assert protobuf_value.double_value == 20.0
    assert protobuf_value.attributes["NI_UnitDescription"].string_value == "volts"


def test___str_scalar___convert___valid_string_scalar_protobuf() -> None:
    python_value = Scalar("value", "volts")

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "string_value"
    assert protobuf_value.string_value == "value"
    assert protobuf_value.attributes["NI_UnitDescription"].string_value == "volts"


def test___scalar_units_unset___convert___protobuf_units_blank() -> None:
    python_value = Scalar(10)

    converter = ScalarConverter()
    protobuf_value = converter.to_protobuf_message(python_value)

    assert protobuf_value.WhichOneof("value") == "sint32_value"
    assert protobuf_value.sint32_value == 10
    assert protobuf_value.attributes["NI_UnitDescription"].string_value == ""


def _units_to_scalar_attribute_map(units: str) -> Mapping[str, attribute_value_pb2.AttributeValue]:
    value = attribute_value_pb2.AttributeValue(string_value=units)
    return {"NI_UnitDescription": value}
