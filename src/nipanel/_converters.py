"""Functions to convert between different data formats."""

from __future__ import annotations

import logging
from typing import Callable, NamedTuple, Union

from google.protobuf import any_pb2, wrappers_pb2
from google.protobuf.message import Message
from typing_extensions import TypeAlias

_logger = logging.getLogger(__name__)


class ConvertibleType(NamedTuple):
    """A Python type that can be converted to and from a protobuf Any."""

    python_type: type
    """The Python type."""

    protobuf_typename: str
    """The protobuf name for the type."""

    protobuf_message: type
    """The protobuf message for the type."""

    protobuf_initializer: Callable[[object], Message]
    """A callable that creates an instance of the protobuf type from a Python object."""


def _bool_to_protobuf(value: object) -> wrappers_pb2.BoolValue:
    """Convert a bool to a protobuf BoolValue."""
    assert isinstance(value, bool), f"Expected bool, got {type(value)}"
    return wrappers_pb2.BoolValue(value=value)


def _bytes_to_protobuf(value: object) -> wrappers_pb2.BytesValue:
    """Convert bytes to a protobuf BytesValue."""
    assert isinstance(value, bytes), f"Expected bytes, got {type(value)}"
    return wrappers_pb2.BytesValue(value=value)


def _float_to_protobuf(value: object) -> wrappers_pb2.DoubleValue:
    """Convert a float to a protobuf DoubleValue."""
    assert isinstance(value, float), f"Expected float, got {type(value)}"
    return wrappers_pb2.DoubleValue(value=value)


def _int_to_protobuf(value: object) -> wrappers_pb2.Int64Value:
    """Convert an int to a protobuf Int64Value."""
    assert isinstance(value, int), f"Expected int, got {type(value)}"
    return wrappers_pb2.Int64Value(value=value)


def _str_to_protobuf(value: object) -> wrappers_pb2.StringValue:
    """Convert a str to a protobuf StringValue."""
    assert isinstance(value, str), f"Expected str, got {type(value)}"
    return wrappers_pb2.StringValue(value=value)


_CONVERTIBLE_TYPES = [
    ConvertibleType(
        python_type=bool,
        protobuf_typename=wrappers_pb2.BoolValue.DESCRIPTOR.full_name,
        protobuf_message=wrappers_pb2.BoolValue,
        protobuf_initializer=_bool_to_protobuf,
    ),
    ConvertibleType(
        python_type=bytes,
        protobuf_typename=wrappers_pb2.BytesValue.DESCRIPTOR.full_name,
        protobuf_message=wrappers_pb2.BytesValue,
        protobuf_initializer=_bytes_to_protobuf,
    ),
    ConvertibleType(
        python_type=float,
        protobuf_typename=wrappers_pb2.DoubleValue.DESCRIPTOR.full_name,
        protobuf_message=wrappers_pb2.DoubleValue,
        protobuf_initializer=_float_to_protobuf,
    ),
    ConvertibleType(
        python_type=int,
        protobuf_typename=wrappers_pb2.Int64Value.DESCRIPTOR.full_name,
        protobuf_message=wrappers_pb2.Int64Value,
        protobuf_initializer=_int_to_protobuf,
    ),
    ConvertibleType(
        python_type=str,
        protobuf_typename=wrappers_pb2.StringValue.DESCRIPTOR.full_name,
        protobuf_message=wrappers_pb2.StringValue,
        protobuf_initializer=_str_to_protobuf,
    ),
]

_PROTOBUF_WRAPPER_FOR_PYTHON_TYPE = {
    entry.python_type: entry.protobuf_initializer for entry in _CONVERTIBLE_TYPES
}

_PROTOBUF_WRAPPER_FOR_GRPC_TYPE = {
    entry.protobuf_typename: entry.protobuf_message for entry in _CONVERTIBLE_TYPES
}

_SUPPORTED_PYTHON_TYPES = _PROTOBUF_WRAPPER_FOR_PYTHON_TYPE.keys()


def to_any(python_value: object) -> any_pb2.Any:
    """Convert a Python object to a protobuf Any."""
    underlying_parents = type(python_value).mro()  # This covers enum.IntEnum and similar

    best_matching_type = next(
        (parent for parent in underlying_parents if parent in _SUPPORTED_PYTHON_TYPES), None
    )
    if not best_matching_type:
        raise TypeError(
            f"Unsupported type: {type(python_value)} with parents {underlying_parents}. Supported types are: {_SUPPORTED_PYTHON_TYPES}"
        )
    _logger.debug(f"Best matching type for '{repr(python_value)}' resolved to {best_matching_type}")

    the_any = any_pb2.Any()
    wrapped_value = _PROTOBUF_WRAPPER_FOR_PYTHON_TYPE[best_matching_type](python_value)
    the_any.Pack(wrapped_value)
    return the_any


def from_any(protobuf_any: any_pb2.Any) -> object:
    """Convert a protobuf Any to a Python object."""
    if not isinstance(protobuf_any, any_pb2.Any):
        raise ValueError(f"Unexpected type: {type(protobuf_any)}")

    underlying_typename = protobuf_any.TypeName()
    _logger.debug(f"Unpacking type '{underlying_typename}'")

    protobuf_wrapper = _PROTOBUF_WRAPPER_FOR_GRPC_TYPE[underlying_typename]()
    did_unpack = protobuf_any.Unpack(protobuf_wrapper)
    if not did_unpack:
        raise ValueError(f"Failed to unpack Any with underlying type '{underlying_typename}'")

    return protobuf_wrapper.value
