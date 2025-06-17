import pytest
from ni.protobuf.types.scalar_pb2 import ScalarData
from nitypes.scalar import Scalar

import nipanel._convert
from google.protobuf import any_pb2, wrappers_pb2


# ========================================================
# Protobuf to Python
# ========================================================
def test___bool___to_any___valid_bool_value() -> None:
    expected_bool = True

    result = nipanel._convert.to_any(expected_bool)
    unpack_dest = wrappers_pb2.BoolValue(value=False)
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, wrappers_pb2.BoolValue)
    assert unpack_dest.value == expected_bool


def test___int___to_any___valid_int_value() -> None:
    expected_int = 123

    result = nipanel._convert.to_any(expected_int)
    unpack_dest = wrappers_pb2.Int64Value(value=0)
    _assert_any_and_unpack(result, unpack_dest)

    assert isinstance(unpack_dest, wrappers_pb2.Int64Value)
    assert unpack_dest.value == expected_int


def _assert_any_and_unpack(packed_message, unpack_destination):
    assert isinstance(packed_message, any_pb2.Any)
    did_unpack = packed_message.Unpack(unpack_destination)
    if not did_unpack:
        raise ValueError(f"Failed to unpack Any with type '{packed_message.TypeName()}'")
