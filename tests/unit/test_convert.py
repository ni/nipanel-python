import pytest
from ni.protobuf.types.scalar_pb2 import ScalarData
from nitypes.scalar import Scalar

import nipanel._convert
from google.protobuf import any_pb2, wrappers_pb2
from nipanel.converters.protobuf_types import ScalarConverter


# ========================================================
# Protobuf to Python
# ========================================================
def test___bool___to_any___valid_bool_value() -> None:
    expected_bool = True

    result = nipanel._convert.to_any(expected_bool)

    assert isinstance(result, any_pb2.Any)
    any_proto = any_pb2.Any()
    assert isinstance(result, wrappers_pb2.BoolValue)
    assert result.
