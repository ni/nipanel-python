"""Functions to convert between different data formats."""

from __future__ import annotations

import logging
from typing import Callable, NamedTuple, Union

import google.protobuf.any_pb2
import google.protobuf.wrappers_pb2
from typing_extensions import TypeAlias

_logger = logging.getLogger(__name__)


_builtin_protobuf_type: TypeAlias = Union[
    google.protobuf.wrappers_pb2.BoolValue,
    google.protobuf.wrappers_pb2.BytesValue,
    google.protobuf.wrappers_pb2.DoubleValue,
    google.protobuf.wrappers_pb2.Int64Value,
    google.protobuf.wrappers_pb2.StringValue,
]


class ConvertibleType(NamedTuple):
    """A Python type that can be converted to and from a protobuf Any."""

    name: str
    """The human name of the type."""

    python_typename: str
    """The Python name for the type."""

    protobuf_typename: str
    """The protobuf name for the type."""

    protobuf_initializer: Callable[..., _builtin_protobuf_type]
    """A callable that can be used to create an instance of the protobuf type."""


_CONVERTIBLE_TYPES: dict[str, ConvertibleType] = {
    "bool": ConvertibleType(
        name="Boolean",
        python_typename=bool.__name__,
        protobuf_typename=google.protobuf.wrappers_pb2.BoolValue.DESCRIPTOR.full_name,
        protobuf_initializer=google.protobuf.wrappers_pb2.BoolValue,
    ),
    "bytes": ConvertibleType(
        name="Bytes",
        python_typename=bytes.__name__,
        protobuf_typename=google.protobuf.wrappers_pb2.BytesValue.DESCRIPTOR.full_name,
        protobuf_initializer=google.protobuf.wrappers_pb2.BytesValue,
    ),
    "float": ConvertibleType(
        name="Float",
        python_typename=float.__name__,
        protobuf_typename=google.protobuf.wrappers_pb2.DoubleValue.DESCRIPTOR.full_name,
        protobuf_initializer=google.protobuf.wrappers_pb2.DoubleValue,
    ),
    "int": ConvertibleType(
        name="Integer",
        python_typename=int.__name__,
        protobuf_typename=google.protobuf.wrappers_pb2.Int64Value.DESCRIPTOR.full_name,
        protobuf_initializer=google.protobuf.wrappers_pb2.Int64Value,
    ),
    "str": ConvertibleType(
        name="String",
        python_typename=str.__name__,
        protobuf_typename=google.protobuf.wrappers_pb2.StringValue.DESCRIPTOR.full_name,
        protobuf_initializer=google.protobuf.wrappers_pb2.StringValue,
    ),
}


def to_any(python_value: object) -> google.protobuf.any_pb2.Any:
    """Convert a Python object to a protobuf Any."""
    protobuf_wrapper_for_type = {
        entry.python_typename: entry.protobuf_initializer for entry in _CONVERTIBLE_TYPES.values()
    }
    supported_types = set(protobuf_wrapper_for_type.keys())
    underlying_parents = [
        parent.__name__
        for parent in type(python_value).mro()  # This covers enum.IntEnum and similar
    ]

    best_matching_type = next(
        (parent for parent in underlying_parents if parent in supported_types), None
    )
    if not best_matching_type:
        raise TypeError(
            f"Unsupported type: {type(python_value)} with parents {underlying_parents}. Supported types are: {supported_types}"
        )
    _logger.debug(f"Best matching type for '{repr(python_value)}' resolved to {best_matching_type}")

    the_any = google.protobuf.any_pb2.Any()
    wrapped_value = protobuf_wrapper_for_type[best_matching_type](value=python_value)
    the_any.Pack(wrapped_value)
    return the_any


def from_any(protobuf_any: google.protobuf.any_pb2.Any) -> object:
    """Convert a protobuf Any to a Python object."""
    protobuf_wrapper_for_type = {
        entry.protobuf_typename: entry.protobuf_initializer for entry in _CONVERTIBLE_TYPES.values()
    }
    if not isinstance(protobuf_any, google.protobuf.any_pb2.Any):
        raise ValueError(f"Unexpected type: {type(protobuf_any)}")

    underlying_typename = protobuf_any.TypeName()
    _logger.debug(f"Unpacking type '{underlying_typename}'")

    protobuf_wrapper = protobuf_wrapper_for_type[underlying_typename]()
    did_unpack = protobuf_any.Unpack(protobuf_wrapper)
    if not did_unpack:
        raise ValueError(f"Failed to unpack Any with underlying type '{underlying_typename}'")

    return protobuf_wrapper.value
