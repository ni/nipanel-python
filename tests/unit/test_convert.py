import datetime as dt
from typing import Any, Collection, Union

import hightime as ht
import nitypes.bintime as bt
import numpy as np
import pytest
from google.protobuf import any_pb2, duration_pb2, timestamp_pb2, wrappers_pb2
from google.protobuf.message import Message
from ni.protobuf.types import (
    array_pb2,
    attribute_value_pb2,
    precision_duration_pb2,
    precision_timestamp_pb2,
    scalar_pb2,
    vector_pb2,
    waveform_pb2,
)
from nitypes.complex import ComplexInt32DType
from nitypes.scalar import Scalar
from nitypes.time import convert_datetime, convert_timedelta
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum
from typing_extensions import TypeAlias

import nipanel._convert
import tests.types

_AnyWrappersPb2: TypeAlias = Union[
    wrappers_pb2.BoolValue,
    wrappers_pb2.BytesValue,
    wrappers_pb2.DoubleValue,
    wrappers_pb2.Int64Value,
    wrappers_pb2.StringValue,
]

_AnyPanelPbTypes: TypeAlias = Union[
    array_pb2.BoolArray,
    array_pb2.BytesArray,
    array_pb2.DoubleArray,
    array_pb2.SInt64Array,
    array_pb2.StringArray,
]


# ========================================================
# _get_best_matching_type() tests
# ========================================================
@pytest.mark.parametrize(
    "python_object, expected_type_string",
    [
        (False, "builtins.bool"),
        (b"mystr", "builtins.bytes"),
        (456.2, "builtins.float"),
        (123, "builtins.int"),
        ("mystr", "builtins.str"),
        (tests.types.MyIntFlags.VALUE1, "builtins.int"),
        (tests.types.MyIntEnum.VALUE10, "builtins.int"),
        (tests.types.MixinIntEnum.VALUE11, "builtins.int"),
        (tests.types.MyStrEnum.VALUE1, "builtins.str"),
        (tests.types.MixinStrEnum.VALUE11, "builtins.str"),
        (dt.datetime.now(), "datetime.datetime"),
        (dt.timedelta(days=1), "datetime.timedelta"),
        (bt.DateTime.now(tz=dt.timezone.utc), "nitypes.bintime.DateTime"),
        (bt.TimeDelta(seconds=1), "nitypes.bintime.TimeDelta"),
        (ht.datetime.now(), "hightime.datetime"),
        (ht.timedelta(days=1), "hightime.timedelta"),
        ([False, False], "collections.abc.Collection[builtins.bool]"),
        ([b"mystr", b"mystr"], "collections.abc.Collection[builtins.bytes]"),
        ([456.2, 1.0], "collections.abc.Collection[builtins.float]"),
        ([123, 456], "collections.abc.Collection[builtins.int]"),
        (["mystr", "mystr"], "collections.abc.Collection[builtins.str]"),
        ((False, False), "collections.abc.Collection[builtins.bool]"),
        ((b"mystr", b"mystr"), "collections.abc.Collection[builtins.bytes]"),
        ((456.2, 1.0), "collections.abc.Collection[builtins.float]"),
        ((123, 456), "collections.abc.Collection[builtins.int]"),
        (("mystr", "mystr"), "collections.abc.Collection[builtins.str]"),
        ((False, False), "collections.abc.Collection[builtins.bool]"),
        ((b"mystr", b"mystr"), "collections.abc.Collection[builtins.bytes]"),
        ((456.2, 1.0), "collections.abc.Collection[builtins.float]"),
        ((123, 456), "collections.abc.Collection[builtins.int]"),
        (("mystr", "mystr"), "collections.abc.Collection[builtins.str]"),
        (set([False, True]), "collections.abc.Collection[builtins.bool]"),
        (set([b"mystr", b"mystr2"]), "collections.abc.Collection[builtins.bytes]"),
        (set([456.2, 1.0]), "collections.abc.Collection[builtins.float]"),
        (set([123, 456]), "collections.abc.Collection[builtins.int]"),
        (set(["mystr", "mystr2"]), "collections.abc.Collection[builtins.str]"),
        (frozenset([False, True]), "collections.abc.Collection[builtins.bool]"),
        (frozenset([b"mystr", b"mystr2"]), "collections.abc.Collection[builtins.bytes]"),
        (frozenset([456.2, 1.0]), "collections.abc.Collection[builtins.float]"),
        (frozenset([123, 456]), "collections.abc.Collection[builtins.int]"),
        (frozenset(["mystr", "mystr2"]), "collections.abc.Collection[builtins.str]"),
        (
            [[1.0, 2.0], [1.0, 2.0]],
            "collections.abc.Collection[collections.abc.Collection[builtins.float]]",
        ),
        (
            [(1.0, 2.0), (3.0, 4.0)],
            "collections.abc.Collection[collections.abc.Collection[builtins.float]]",
        ),
        (
            [set([1.0, 2.0]), set([3.0, 4.0])],
            "collections.abc.Collection[collections.abc.Collection[builtins.float]]",
        ),
        (
            [frozenset([1.0, 2.0]), frozenset([3.0, 4.0])],
            "collections.abc.Collection[collections.abc.Collection[builtins.float]]",
        ),
        (
            ([1.0, 2.0], [3.0, 4.0]),
            "collections.abc.Collection[collections.abc.Collection[builtins.float]]",
        ),
        (
            ((1.0, 2.0), (3.0, 4.0)),
            "collections.abc.Collection[collections.abc.Collection[builtins.float]]",
        ),
        (
            (set([1.0, 2.0]), set([3.0, 4.0])),
            "collections.abc.Collection[collections.abc.Collection[builtins.float]]",
        ),
        (
            (frozenset([1.0, 2.0]), frozenset([3.0, 4.0])),
            "collections.abc.Collection[collections.abc.Collection[builtins.float]]",
        ),
        (
            set([(1.0, 2.0), (3.0, 4.0)]),
            "collections.abc.Collection[collections.abc.Collection[builtins.float]]",
        ),
        (
            set([frozenset([1.0, 2.0]), frozenset([3.0, 4.0])]),
            "collections.abc.Collection[collections.abc.Collection[builtins.float]]",
        ),
        (
            frozenset([(1.0, 2.0), (3.0, 4.0)]),
            "collections.abc.Collection[collections.abc.Collection[builtins.float]]",
        ),
        (
            frozenset([frozenset([1.0, 2.0]), frozenset([3.0, 4.0])]),
            "collections.abc.Collection[collections.abc.Collection[builtins.float]]",
        ),
        (AnalogWaveform(0, np.int16), "nitypes.waveform.AnalogWaveform[int16]"),
        (AnalogWaveform(0, np.float64), "nitypes.waveform.AnalogWaveform[float64]"),
        (ComplexWaveform(0, np.complex128), "nitypes.waveform.ComplexWaveform[complex128]"),
        (
            ComplexWaveform(0, ComplexInt32DType),
            "nitypes.waveform.ComplexWaveform[[('real', '<i2'), ('imag', '<i2')]]",
        ),
        (DigitalWaveform(10, 2, np.bool, False), "nitypes.waveform.DigitalWaveform"),
        (Spectrum(10, np.float64), "nitypes.waveform.Spectrum"),
        (Scalar("one"), "nitypes.scalar.Scalar"),
        (Vector([1, 2, 3]), "nitypes.vector.Vector"),
    ],
)
def test___various_python_objects___get_best_matching_type___returns_correct_type_string(
    python_object: object, expected_type_string: str
) -> None:
    type_string = nipanel._convert._get_best_matching_type(python_object)
    assert type_string == expected_type_string


# ========================================================
# Built-in Types: Python to Protobuf
# ========================================================
@pytest.mark.parametrize(
    "proto_type, default_value, expected_value",
    [
        (wrappers_pb2.BoolValue, False, True),
        (wrappers_pb2.BytesValue, b"", b"mystr"),
        (wrappers_pb2.DoubleValue, 0.0, 456.2),
        (wrappers_pb2.Int64Value, 0, 123),
        (wrappers_pb2.StringValue, "", "mystr"),
    ],
)
def test___python_builtin_scalar___to_any___valid_wrapperpb2_value(
    proto_type: type[_AnyWrappersPb2], default_value: Any, expected_value: Any
) -> None:
    result = nipanel._convert.to_any(expected_value)
    unpack_dest = proto_type(value=default_value)
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, proto_type)
    assert unpack_dest.value == expected_value


def test___python_datetime_datetime___to_any___valid_timestamppb2_value() -> None:
    expected_value = dt.datetime.now()
    result = nipanel._convert.to_any(expected_value)
    unpack_dest = timestamp_pb2.Timestamp()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, timestamp_pb2.Timestamp)
    assert unpack_dest.ToDatetime() == expected_value


def test___python_datetime_timedelta___to_any___valid_durationpb2_value() -> None:
    expected_value = dt.timedelta(days=1, seconds=2, microseconds=3)
    result = nipanel._convert.to_any(expected_value)
    unpack_dest = duration_pb2.Duration()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, duration_pb2.Duration)
    assert unpack_dest.ToTimedelta() == expected_value


def test___none_value___to_any___raises_type_error() -> None:
    """Test that passing None to to_any() raises a TypeError."""
    with pytest.raises(TypeError):
        nipanel._convert.to_any(None)


# ========================================================
# Built-in Types: Protobuf to Python
# ========================================================
@pytest.mark.parametrize(
    "proto_type, expected_value",
    [
        (wrappers_pb2.BoolValue, True),
        (wrappers_pb2.BytesValue, b"mystr"),
        (wrappers_pb2.DoubleValue, 456.2),
        (wrappers_pb2.Int64Value, 123),
        (wrappers_pb2.StringValue, "mystr"),
    ],
)
def test___wrapperpb2_value___from_any___valid_python_value(
    proto_type: type[_AnyWrappersPb2], expected_value: Any
) -> None:
    pb_value = proto_type(value=expected_value)
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, type(expected_value))
    assert result == expected_value


def test___timestamppb2_timestamp___from_any___valid_python_value() -> None:
    expected_value = dt.datetime.now()
    pb_value = timestamp_pb2.Timestamp()
    pb_value.FromDatetime(expected_value)
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, dt.datetime)
    assert result == expected_value


def test___durationpb2_timestamp___from_any___valid_python_value() -> None:
    expected_value = dt.timedelta(weeks=1, hours=2, minutes=3)
    pb_value = duration_pb2.Duration()
    pb_value.FromTimedelta(expected_value)
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, dt.timedelta)
    assert result == expected_value


# ========================================================
# Protobuf Types: Python to Protobuf
# ========================================================
@pytest.mark.parametrize(
    "proto_type, default_value, expected_value",
    [
        (array_pb2.BoolArray, [False, False, False], [True, True, True]),
        (array_pb2.BytesArray, [b"", b"", b""], [b"a", b"b", b"c"]),
        (array_pb2.DoubleArray, [0.0, 0.0, 0.0], [1.0, 2.0, 3.0]),
        (array_pb2.SInt64Array, [0, 0, 0], [1, 2, 3]),
        (array_pb2.StringArray, ["", "", ""], ["a", "b", "c"]),
    ],
)
def test___python_collection___to_any___valid_array_proto(
    proto_type: type[_AnyPanelPbTypes], default_value: Any, expected_value: Any
) -> None:
    result = nipanel._convert.to_any(expected_value)
    unpack_dest = proto_type(values=default_value)
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, proto_type)
    assert unpack_dest.values == expected_value


def test___python_scalar_object___to_any___valid_scalar_proto() -> None:
    scalar_obj = Scalar(1.0, "amps")
    result = nipanel._convert.to_any(scalar_obj)
    unpack_dest = scalar_pb2.Scalar()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, scalar_pb2.Scalar)
    assert unpack_dest.double_value == 1.0
    assert unpack_dest.attributes["NI_UnitDescription"].string_value == "amps"


def test___python_vector_object___to_any___valid_vector_proto() -> None:
    vector_obj = Vector([1.0, 2.0, 3.0], "amps")
    result = nipanel._convert.to_any(vector_obj)
    unpack_dest = vector_pb2.Vector()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, vector_pb2.Vector)
    assert list(unpack_dest.double_array.values) == [1.0, 2.0, 3.0]
    assert unpack_dest.attributes["NI_UnitDescription"].string_value == "amps"


def test___python_float64_analog_waveform___to_any___valid_double_analog_waveform_proto() -> None:
    wfm_obj = AnalogWaveform(3, np.float64)
    result = nipanel._convert.to_any(wfm_obj)
    unpack_dest = waveform_pb2.DoubleAnalogWaveform()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, waveform_pb2.DoubleAnalogWaveform)
    assert list(unpack_dest.y_data) == [0.0, 0.0, 0.0]


def test___python_int16_analog_waveform___to_any___valid_i16_analog_waveform_proto() -> None:
    wfm_obj = AnalogWaveform(3, np.int16)
    result = nipanel._convert.to_any(wfm_obj)
    unpack_dest = waveform_pb2.I16AnalogWaveform()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, waveform_pb2.I16AnalogWaveform)
    assert list(unpack_dest.y_data) == [0, 0, 0]


def test___python_float64_complex_waveform___to_any___valid_double_complex_waveform_proto() -> None:
    wfm_obj = ComplexWaveform(2, np.complex128)
    result = nipanel._convert.to_any(wfm_obj)
    unpack_dest = waveform_pb2.DoubleComplexWaveform()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, waveform_pb2.DoubleComplexWaveform)
    assert list(unpack_dest.y_data) == [0.0, 0.0, 0.0, 0.0]


def test___python_int16_complex_waveform___to_any___valid_i16_complex_waveform_proto() -> None:
    wfm_obj = ComplexWaveform(2, ComplexInt32DType)
    result = nipanel._convert.to_any(wfm_obj)
    unpack_dest = waveform_pb2.I16ComplexWaveform()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, waveform_pb2.I16ComplexWaveform)
    assert list(unpack_dest.y_data) == [0, 0, 0, 0]


def test___python_bool_digital_waveform___to_any___valid_digital_waveform_proto() -> None:
    data = np.array([[0, 1, 0], [1, 0, 1]], dtype=np.bool)
    wfm_obj = DigitalWaveform.from_lines(data, signal_count=3)

    result = nipanel._convert.to_any(wfm_obj)
    unpack_dest = waveform_pb2.DigitalWaveform()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, waveform_pb2.DigitalWaveform)
    assert unpack_dest.y_data == b"\x00\x01\x00\x01\x00\x01"
    assert unpack_dest.signal_count == 3


def test___python_uint8_digital_waveform___to_any___valid_digital_waveform_proto() -> None:
    data = np.array([[0, 1, 3], [7, 5, 1]], dtype=np.uint8)
    wfm_obj = DigitalWaveform.from_lines(data, signal_count=3)

    result = nipanel._convert.to_any(wfm_obj)
    unpack_dest = waveform_pb2.DigitalWaveform()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, waveform_pb2.DigitalWaveform)
    assert unpack_dest.y_data == b"\x00\x01\x03\x07\x05\x01"
    assert unpack_dest.signal_count == 3


def test___python_float64_spectrum___to_any___valid_double_spectrum_proto() -> None:
    spectrum = Spectrum.from_array_1d(np.array([1.0, 2.0, 3.0]))
    spectrum.start_frequency = 100.0
    spectrum.frequency_increment = 10.0

    result = nipanel._convert.to_any(spectrum)
    unpack_dest = waveform_pb2.DoubleSpectrum()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, waveform_pb2.DoubleSpectrum)
    assert list(unpack_dest.data) == [1.0, 2.0, 3.0]
    assert unpack_dest.start_frequency == 100.0
    assert unpack_dest.frequency_increment == 10.0


def test___python_bintime_datetime__to_any___valid_precision_timestamp_proto() -> None:
    python_value = bt.DateTime(year=2020, month=1, day=10, second=45, tzinfo=dt.timezone.utc)

    result = nipanel._convert.to_any(python_value)
    unpack_dest = precision_timestamp_pb2.PrecisionTimestamp()
    _assert_any_and_unpack(result, unpack_dest)

    expected_tuple = python_value.to_tuple()
    assert unpack_dest.seconds == expected_tuple.whole_seconds
    assert unpack_dest.fractional_seconds == expected_tuple.fractional_seconds


def test___python_bintime_timedelta__to_any___valid_precision_duration_proto() -> None:
    python_value = bt.TimeDelta(seconds=12.345)

    result = nipanel._convert.to_any(python_value)
    unpack_dest = precision_duration_pb2.PrecisionDuration()
    _assert_any_and_unpack(result, unpack_dest)

    expected_tuple = python_value.to_tuple()
    assert unpack_dest.seconds == expected_tuple.whole_seconds
    assert unpack_dest.fractional_seconds == expected_tuple.fractional_seconds


def test___python_hightime_datetime__to_any___valid_precision_timestamp_proto() -> None:
    python_value = ht.datetime(year=2020, month=1, day=10, second=45, tzinfo=dt.timezone.utc)

    result = nipanel._convert.to_any(python_value)
    unpack_dest = precision_timestamp_pb2.PrecisionTimestamp()
    _assert_any_and_unpack(result, unpack_dest)

    expected_bt_datetime = convert_datetime(bt.DateTime, python_value)
    expected_tuple = expected_bt_datetime.to_tuple()
    assert unpack_dest.seconds == expected_tuple.whole_seconds
    assert unpack_dest.fractional_seconds == expected_tuple.fractional_seconds


def test___python_hightime_timedelta__to_any___valid_precision_duration_proto() -> None:
    python_value = ht.timedelta(days=10, seconds=45, picoseconds=60)

    result = nipanel._convert.to_any(python_value)
    unpack_dest = precision_duration_pb2.PrecisionDuration()
    _assert_any_and_unpack(result, unpack_dest)

    expected_bt_timedelta = convert_timedelta(bt.TimeDelta, python_value)
    expected_tuple = expected_bt_timedelta.to_tuple()
    assert unpack_dest.seconds == expected_tuple.whole_seconds
    assert unpack_dest.fractional_seconds == expected_tuple.fractional_seconds


@pytest.mark.parametrize(
    "python_value",
    [
        # lists of collections
        ([[1.0, 2.0], [3.0, 4.0]]),
        ([(1.0, 2.0), (3.0, 4.0)]),
        ([set([1.0, 2.0]), set([3.0, 4.0])]),
        ([frozenset([1.0, 2.0]), frozenset([3.0, 4.0])]),
        # tuples of collections
        (([1.0, 2.0], [3.0, 4.0])),
        (((1.0, 2.0), (3.0, 4.0))),
        ((set([1.0, 2.0]), set([3.0, 4.0]))),
        ((frozenset([1.0, 2.0]), frozenset([3.0, 4.0]))),
    ],
)
def test___python_2dcollection_of_float___to_any___valid_double2darray(
    python_value: Collection[Collection[float]],
) -> None:
    expected_data = [1.0, 2.0, 3.0, 4.0]
    expected_rows = 2
    expected_columns = 2
    result = nipanel._convert.to_any(python_value)
    unpack_dest = array_pb2.Double2DArray()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, array_pb2.Double2DArray)
    assert unpack_dest.rows == expected_rows
    assert unpack_dest.columns == expected_columns
    assert unpack_dest.data == expected_data


@pytest.mark.parametrize(
    "python_value",
    [
        (set([(1.0, 2.0), (3.0, 4.0)])),
        (set([frozenset([1.0, 2.0]), frozenset([3.0, 4.0])])),
        (frozenset([(1.0, 2.0), (3.0, 4.0)])),
        (frozenset([frozenset([1.0, 2.0]), frozenset([3.0, 4.0])])),
    ],
)
def test___python_set_of_collection_of_float___to_any___valid_double2darray(
    python_value: Collection[Collection[float]],
) -> None:
    expected_data = [1.0, 2.0, 3.0, 4.0]
    expected_rows = 2
    expected_columns = 2
    result = nipanel._convert.to_any(python_value)
    unpack_dest = array_pb2.Double2DArray()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, array_pb2.Double2DArray)
    assert unpack_dest.rows == expected_rows
    assert unpack_dest.columns == expected_columns
    # Sets and frozensets don't maintain order, so sort before comparing.
    assert sorted(unpack_dest.data) == sorted(expected_data)


# ========================================================
# Protobuf Types: Protobuf to Python
# ========================================================
@pytest.mark.parametrize(
    "proto_type, expected_value",
    [
        (array_pb2.BoolArray, [True, True, True]),
        (array_pb2.BytesArray, [b"a", b"b", b"c"]),
        (array_pb2.DoubleArray, [1.0, 2.0, 3.0]),
        (array_pb2.SInt64Array, [1, 2, 3]),
        (array_pb2.StringArray, ["a", "b", "c"]),
    ],
)
def test___array_proto___from_any___valid_python_collection(
    proto_type: type[_AnyPanelPbTypes], expected_value: Any
) -> None:
    pb_value = proto_type(values=expected_value)
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, type(expected_value))
    assert result == expected_value


def test___scalar_proto___from_any___valid_python_scalar() -> None:
    attrs = {"NI_UnitDescription": attribute_value_pb2.AttributeValue(string_value="amps")}
    pb_value = scalar_pb2.Scalar(attributes=attrs, double_value=1.0)
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, Scalar)
    assert result.value == 1.0
    assert result.units == "amps"


def test___vector_proto___from_any___valid_python_vector() -> None:
    attrs = {"NI_UnitDescription": attribute_value_pb2.AttributeValue(string_value="amps")}
    pb_value = vector_pb2.Vector(
        attributes=attrs,
        double_array=array_pb2.DoubleArray(values=[1.0, 2.0, 3.0]),
    )
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, Vector)
    assert list(result) == [1.0, 2.0, 3.0]
    assert result.units == "amps"


def test___double_analog_waveform_proto___from_any___valid_python_float64_analog_waveform() -> None:
    pb_value = waveform_pb2.DoubleAnalogWaveform(y_data=[0.0, 0.0, 0.0])
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, AnalogWaveform)
    assert result.sample_count == result.capacity == len(result.raw_data) == 3
    assert result.dtype == np.float64


def test___i16_analog_waveform_proto___from_any___valid_python_int16_analog_waveform() -> None:
    pb_value = waveform_pb2.I16AnalogWaveform(y_data=[0, 0, 0])
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, AnalogWaveform)
    assert result.sample_count == result.capacity == len(result.raw_data) == 3
    assert result.dtype == np.int16


def test___double_complex_waveform_proto___from_any___valid_python_float64_complex_waveform() -> (
    None
):
    pb_value = waveform_pb2.DoubleComplexWaveform(y_data=[0.0, 0.0, 0.0, 0.0])
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, ComplexWaveform)
    assert result.sample_count == result.capacity == len(result.raw_data) == 2
    assert result.dtype == np.complex128


def test___i16_complex_waveform_proto___from_any___valid_python_int16_complex_waveform() -> None:
    pb_value = waveform_pb2.I16ComplexWaveform(y_data=[0, 0, 0, 0])
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, ComplexWaveform)
    assert result.sample_count == result.capacity == len(result.raw_data) == 2
    assert result.dtype == ComplexInt32DType


def test___digital_waveform_proto___from_any___valid_python_bool_digital_waveform() -> None:
    data = np.array([[0, 1, 0], [1, 0, 1]], dtype=np.bool)
    pb_value = waveform_pb2.DigitalWaveform(y_data=data.tobytes(), signal_count=3)
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, DigitalWaveform)
    assert np.array_equal(result.data, data)
    assert result.signal_count == 3


def test___digital_waveform_proto___from_any___valid_python_uint8_digital_waveform() -> None:
    data = np.array([[0, 1, 0], [1, 0, 1]], dtype=np.uint8)
    pb_value = waveform_pb2.DigitalWaveform(y_data=data.tobytes(), signal_count=3)
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, DigitalWaveform)
    assert np.array_equal(result.data, data)
    assert result.signal_count == 3


def test___double_spectrum_proto___from_any___valid_python_spectrum() -> None:
    pb_value = waveform_pb2.DoubleSpectrum(
        data=[1.0, 2.0, 3.0],
        start_frequency=100.0,
        frequency_increment=10.0,
    )
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, Spectrum)
    assert list(result.data) == [1.0, 2.0, 3.0]
    assert result.start_frequency == 100.0
    assert result.frequency_increment == 10.0


def test___precision_timestamp_proto__from_any___valid_bintime_datetime() -> None:
    expected_bt_dt = bt.DateTime(year=2020, month=1, day=10, second=45, tzinfo=dt.timezone.utc)
    expected_tuple = expected_bt_dt.to_tuple()
    pb_value = precision_timestamp_pb2.PrecisionTimestamp(
        seconds=expected_tuple.whole_seconds,
        fractional_seconds=expected_tuple.fractional_seconds,
    )
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, bt.DateTime)
    assert result == expected_bt_dt


def test___precision_duration_proto__from_any___valid_bintime_timedelta() -> None:
    expected_bt_td = bt.TimeDelta(seconds=45.678)
    expected_tuple = expected_bt_td.to_tuple()
    pb_value = precision_duration_pb2.PrecisionDuration(
        seconds=expected_tuple.whole_seconds,
        fractional_seconds=expected_tuple.fractional_seconds,
    )
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, bt.TimeDelta)
    assert result == expected_bt_td


def test___double2darray___from_any___valid_python_2dcollection() -> None:
    pb_value = array_pb2.Double2DArray(data=[1.0, 2.0, 3.0, 4.0], rows=2, columns=2)
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    expected_value = [[1.0, 2.0], [3.0, 4.0]]
    assert isinstance(result, type(expected_value))
    assert result == expected_value


# ========================================================
# Pack/Unpack Helpers
# ========================================================
def _assert_any_and_unpack(packed_message: any_pb2.Any, unpack_destination: Message) -> None:
    assert isinstance(packed_message, any_pb2.Any)
    assert packed_message.Unpack(unpack_destination)


def _pack_into_any(proto_value: Message) -> any_pb2.Any:
    as_any = any_pb2.Any()
    as_any.Pack(proto_value)
    return as_any
