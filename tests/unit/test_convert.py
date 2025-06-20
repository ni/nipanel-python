from typing import Any, Union

import numpy as np
import pytest
from google.protobuf import any_pb2, wrappers_pb2
from google.protobuf.message import Message
from ni.protobuf.types.scalar_pb2 import ScalarData
from ni.pythonpanel.v1 import python_panel_types_pb2
from ni_measurement_plugin_sdk_service._internal.stubs.ni.protobuf.types.waveform_pb2 import (
    DoubleAnalogWaveform,
)
from nitypes.scalar import Scalar
from nitypes.waveform import AnalogWaveform
from typing_extensions import TypeAlias

import nipanel._convert


_AnyWrappersPb2: TypeAlias = Union[
    wrappers_pb2.BoolValue,
    wrappers_pb2.BytesValue,
    wrappers_pb2.DoubleValue,
    wrappers_pb2.Int64Value,
    wrappers_pb2.StringValue,
]

_AnyPanelPbTypes: TypeAlias = Union[
    python_panel_types_pb2.BoolCollection,
    python_panel_types_pb2.ByteStringCollection,
    python_panel_types_pb2.FloatCollection,
    python_panel_types_pb2.IntCollection,
    python_panel_types_pb2.StringCollection,
]


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


@pytest.mark.parametrize(
    "proto_type, default_value, expected_value",
    [
        (python_panel_types_pb2.BoolCollection, [False, False, False], [True, True, True]),
        (python_panel_types_pb2.ByteStringCollection, [b"", b"", b""], [b"a", b"b", b"c"]),
        (python_panel_types_pb2.FloatCollection, [0.0, 0.0, 0.0], [1.0, 2.0, 3.0]),
        (python_panel_types_pb2.IntCollection, [0, 0, 0], [1, 2, 3]),
        (python_panel_types_pb2.StringCollection, ["", "", ""], ["a", "b", "c"]),
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


@pytest.mark.parametrize(
    "proto_type, expected_value",
    [
        (python_panel_types_pb2.BoolCollection, [True, True, True]),
        (python_panel_types_pb2.ByteStringCollection, [b"a", b"b", b"c"]),
        (python_panel_types_pb2.FloatCollection, [1.0, 2.0, 3.0]),
        (python_panel_types_pb2.IntCollection, [1, 2, 3]),
        (python_panel_types_pb2.StringCollection, ["a", "b", "c"]),
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
