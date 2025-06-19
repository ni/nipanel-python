from typing import Any, Type, Union

import pytest
from google.protobuf import any_pb2, wrappers_pb2
from ni.pythonpanel.v1 import python_panel_types_pb2
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
# Python to Protobuf
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
    proto_type: Type[_AnyWrappersPb2], default_value: Any, expected_value: Any
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
    proto_type: Type[_AnyPanelPbTypes], default_value: Any, expected_value: Any
) -> None:
    result = nipanel._convert.to_any(expected_value)
    unpack_dest = proto_type(values=default_value)
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, proto_type)
    assert unpack_dest.values == expected_value


# ========================================================
# Protobuf to Python
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
    proto_type: Type[_AnyWrappersPb2], expected_value: Any
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
    proto_type: Type[_AnyPanelPbTypes], expected_value: Any
) -> None:
    pb_value = proto_type(values=expected_value)
    packed_any = _pack_into_any(pb_value)

    result = nipanel._convert.from_any(packed_any)

    assert isinstance(result, type(expected_value))
    assert result == expected_value


# ========================================================
# Pack/Unpack Helpers
# ========================================================
def _assert_any_and_unpack(packed_message: any_pb2.Any, unpack_destination: Any) -> None:
    assert isinstance(packed_message, any_pb2.Any)
    assert packed_message.Unpack(unpack_destination)


def _pack_into_any(proto_value: Union[_AnyWrappersPb2, _AnyPanelPbTypes]) -> any_pb2.Any:
    as_any = any_pb2.Any()
    as_any.Pack(proto_value)
    return as_any
