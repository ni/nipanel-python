"""Functions to convert between different data formats."""

from __future__ import annotations

import logging
from typing import Callable, NamedTuple, Union

from google.protobuf import any_pb2, wrappers_pb2
from typing_extensions import TypeAlias

_logger = logging.getLogger(__name__)


_builtin_protobuf_type: TypeAlias = Union[
    wrappers_pb2.BoolValue,
    wrappers_pb2.BytesValue,
    wrappers_pb2.DoubleValue,
    wrappers_pb2.Int64Value,
    wrappers_pb2.StringValue,
]


class ConvertibleType(NamedTuple):
    """A Python type that can be converted to and from a protobuf Any."""

    python_type: type
    """The Python type."""

    protobuf_typename: str
    """The protobuf name for the type."""

    protobuf_initializer: Callable[..., _builtin_protobuf_type]
    """A callable that can be used to create an instance of the protobuf type."""


_CONVERTIBLE_TYPES = [
    ConvertibleType(
        python_type=bool,
        protobuf_typename=wrappers_pb2.BoolValue.DESCRIPTOR.full_name,
        protobuf_initializer=wrappers_pb2.BoolValue,
    ),
    ConvertibleType(
        python_type=bytes,
        protobuf_typename=wrappers_pb2.BytesValue.DESCRIPTOR.full_name,
        protobuf_initializer=wrappers_pb2.BytesValue,
    ),
    ConvertibleType(
        python_type=float,
        protobuf_typename=wrappers_pb2.DoubleValue.DESCRIPTOR.full_name,
        protobuf_initializer=wrappers_pb2.DoubleValue,
    ),
    ConvertibleType(
        python_type=int,
        protobuf_typename=wrappers_pb2.Int64Value.DESCRIPTOR.full_name,
        protobuf_initializer=wrappers_pb2.Int64Value,
    ),
    ConvertibleType(
        python_type=str,
        protobuf_typename=wrappers_pb2.StringValue.DESCRIPTOR.full_name,
        protobuf_initializer=wrappers_pb2.StringValue,
    ),
]

_PROTOBUF_WRAPPER_FOR_PYTHON_TYPE = {
    entry.python_type: entry.protobuf_initializer for entry in _CONVERTIBLE_TYPES
}

_PROTOBUF_WRAPPER_FOR_GRPC_TYPE = {
    entry.protobuf_typename: entry.protobuf_initializer for entry in _CONVERTIBLE_TYPES
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
    wrapped_value = _PROTOBUF_WRAPPER_FOR_PYTHON_TYPE[best_matching_type](value=python_value)
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
