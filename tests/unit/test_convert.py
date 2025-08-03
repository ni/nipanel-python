import datetime as dt
from typing import Any, Collection, Union

import numpy as np
import pytest
from google.protobuf import any_pb2, timestamp_pb2, wrappers_pb2
from google.protobuf.message import Message
from ni.panels.v1 import panel_types_pb2
from ni.protobuf.types.scalar_pb2 import ScalarData
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.array_pb2 import (
    Double2DArray,
)
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.waveform_pb2 import (
    DoubleAnalogWaveform,
)
from nitypes.scalar import Scalar
from nitypes.waveform import AnalogWaveform
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
    panel_types_pb2.BoolCollection,
    panel_types_pb2.ByteStringCollection,
    panel_types_pb2.FloatCollection,
    panel_types_pb2.IntCollection,
    panel_types_pb2.StringCollection,
]


# ========================================================
# _get_best_matching_type() tests
# ========================================================
@pytest.mark.parametrize(
    "python_object, expected_type_string",
    [
        (False, "bool"),
        (b"mystr", "bytes"),
        (456.2, "float"),
        (123, "int"),
        ("mystr", "str"),
        (tests.types.MyIntFlags.VALUE1, "int"),
        (tests.types.MyIntEnum.VALUE10, "int"),
        (tests.types.MixinIntEnum.VALUE11, "int"),
        (tests.types.MyStrEnum.VALUE1, "str"),
        (tests.types.MixinStrEnum.VALUE11, "str"),
        (dt.datetime.now(), "datetime.datetime"),
        ([False, False], "Collection.bool"),
        ([b"mystr", b"mystr"], "Collection.bytes"),
        ([456.2, 1.0], "Collection.float"),
        ([123, 456], "Collection.int"),
        (["mystr", "mystr"], "Collection.str"),
        ((False, False), "Collection.bool"),
        ((b"mystr", b"mystr"), "Collection.bytes"),
        ((456.2, 1.0), "Collection.float"),
        ((123, 456), "Collection.int"),
        (("mystr", "mystr"), "Collection.str"),
        ((False, False), "Collection.bool"),
        ((b"mystr", b"mystr"), "Collection.bytes"),
        ((456.2, 1.0), "Collection.float"),
        ((123, 456), "Collection.int"),
        (("mystr", "mystr"), "Collection.str"),
        (set([False, True]), "Collection.bool"),
        (set([b"mystr", b"mystr2"]), "Collection.bytes"),
        (set([456.2, 1.0]), "Collection.float"),
        (set([123, 456]), "Collection.int"),
        (set(["mystr", "mystr2"]), "Collection.str"),
        (frozenset([False, True]), "Collection.bool"),
        (frozenset([b"mystr", b"mystr2"]), "Collection.bytes"),
        (frozenset([456.2, 1.0]), "Collection.float"),
        (frozenset([123, 456]), "Collection.int"),
        (frozenset(["mystr", "mystr2"]), "Collection.str"),
        ([[1.0, 2.0], [1.0, 2.0]], "Collection.Collection.float"),
        ([(1.0, 2.0), (3.0, 4.0)], "Collection.Collection.float"),
        ([set([1.0, 2.0]), set([3.0, 4.0])], "Collection.Collection.float"),
        ([frozenset([1.0, 2.0]), frozenset([3.0, 4.0])], "Collection.Collection.float"),
        (([1.0, 2.0], [3.0, 4.0]), "Collection.Collection.float"),
        (((1.0, 2.0), (3.0, 4.0)), "Collection.Collection.float"),
        ((set([1.0, 2.0]), set([3.0, 4.0])), "Collection.Collection.float"),
        ((frozenset([1.0, 2.0]), frozenset([3.0, 4.0])), "Collection.Collection.float"),
        (set([(1.0, 2.0), (3.0, 4.0)]), "Collection.Collection.float"),
        (set([frozenset([1.0, 2.0]), frozenset([3.0, 4.0])]), "Collection.Collection.float"),
        (frozenset([(1.0, 2.0), (3.0, 4.0)]), "Collection.Collection.float"),
        (frozenset([frozenset([1.0, 2.0]), frozenset([3.0, 4.0])]), "Collection.Collection.float"),
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


@pytest.mark.parametrize(
    "proto_type, default_value, expected_value",
    [
        (panel_types_pb2.BoolCollection, [False, False, False], [True, True, True]),
        (panel_types_pb2.ByteStringCollection, [b"", b"", b""], [b"a", b"b", b"c"]),
        (panel_types_pb2.FloatCollection, [0.0, 0.0, 0.0], [1.0, 2.0, 3.0]),
        (panel_types_pb2.IntCollection, [0, 0, 0], [1, 2, 3]),
        (panel_types_pb2.StringCollection, ["", "", ""], ["a", "b", "c"]),
    ],
)
def test___python_panel_collection___to_any___valid_paneltype_value(
    proto_type: type[_AnyPanelPbTypes], default_value: Any, expected_value: Any
) -> None:
    result = nipanel._convert.to_any(expected_value)
    unpack_dest = proto_type(values=default_value)
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, proto_type)
    assert unpack_dest.values == expected_value


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


@pytest.mark.parametrize(
    "proto_type, expected_value",
    [
        (panel_types_pb2.BoolCollection, [True, True, True]),
        (panel_types_pb2.ByteStringCollection, [b"a", b"b", b"c"]),
        (panel_types_pb2.FloatCollection, [1.0, 2.0, 3.0]),
        (panel_types_pb2.IntCollection, [1, 2, 3]),
        (panel_types_pb2.StringCollection, ["a", "b", "c"]),
    ],
)
def test___paneltype_value___from_any___valid_python_value(
    proto_type: type[_AnyPanelPbTypes], expected_value: Any
) -> None:
    pb_value = proto_type(values=expected_value)
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, type(expected_value))
    assert result == expected_value


# ========================================================
# Protobuf Types: Python to Protobuf
# ========================================================
def test___python_scalar_object___to_any___valid_scalar_data_value() -> None:
    scalar_obj = Scalar(1.0, "amps")
    result = nipanel._convert.to_any(scalar_obj)
    unpack_dest = ScalarData()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, ScalarData)
    assert unpack_dest.double_value == 1.0
    assert unpack_dest.units == "amps"


def test___python_analog_waveform___to_any___valid_double_analog_waveform() -> None:
    wfm_obj = AnalogWaveform(3)
    result = nipanel._convert.to_any(wfm_obj)
    unpack_dest = DoubleAnalogWaveform()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, DoubleAnalogWaveform)
    assert list(unpack_dest.y_data) == [0.0, 0.0, 0.0]


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
    unpack_dest = Double2DArray()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, Double2DArray)
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
    unpack_dest = Double2DArray()
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, Double2DArray)
    assert unpack_dest.rows == expected_rows
    assert unpack_dest.columns == expected_columns
    # Sets and frozensets don't maintain order, so sort before comparing.
    assert sorted(unpack_dest.data) == sorted(expected_data)


# ========================================================
# Protobuf Types: Protobuf to Python
# ========================================================
def test___scalar_data___from_any___valid_python_scalar_object() -> None:
    pb_value = ScalarData(units="amps", double_value=1.0)
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, Scalar)
    assert result.value == 1.0
    assert result.units == "amps"


def test___double_analog_waveform___from_any___valid_python_analog_waveform() -> None:
    pb_value = DoubleAnalogWaveform(y_data=[0.0, 0.0, 0.0])
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, AnalogWaveform)
    assert result.sample_count == result.capacity == len(result.raw_data) == 3
    assert result.dtype == np.float64


def test___double2darray___from_any___valid_python_2dcollection() -> None:
    pb_value = Double2DArray(data=[1.0, 2.0, 3.0, 4.0], rows=2, columns=2)
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
