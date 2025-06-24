"""Functions to convert between different data formats."""

from __future__ import annotations

import logging
from collections.abc import Collection
from typing import Any

from google.protobuf import any_pb2

from nipanel.converters import Converter
from nipanel.converters.builtin import (
    BoolConverter,
    BytesConverter,
    FloatConverter,
    IntConverter,
    StrConverter,
    BoolCollectionConverter,
    BytesCollectionConverter,
    FloatCollectionConverter,
    IntCollectionConverter,
    StrCollectionConverter,
)
from nipanel.converters.protobuf_types import DoubleAnalogWaveformConverter, ScalarConverter

_logger = logging.getLogger(__name__)

# FFV -- consider adding a RegisterConverter mechanism
_CONVERTIBLE_TYPES: list[Converter[Any, Any]] = [
    # Scalars first
    BoolConverter(),
    BytesConverter(),
    FloatConverter(),
    IntConverter(),
    StrConverter(),
    # Containers next
    BoolCollectionConverter(),
    BytesCollectionConverter(),
    FloatCollectionConverter(),
    IntCollectionConverter(),
    StrCollectionConverter(),
    # Protobuf Types
    DoubleAnalogWaveformConverter(),
    ScalarConverter(),
]

_CONVERTIBLE_COLLECTION_TYPES = {
    frozenset,
    list,
    set,
    tuple,
}

_CONVERTER_FOR_PYTHON_TYPE = {entry.python_typename: entry for entry in _CONVERTIBLE_TYPES}
_CONVERTER_FOR_GRPC_TYPE = {entry.protobuf_typename: entry for entry in _CONVERTIBLE_TYPES}
_SUPPORTED_PYTHON_TYPES = _CONVERTER_FOR_PYTHON_TYPE.keys()


def to_any(python_value: object) -> any_pb2.Any:
    """Convert a Python object to a protobuf Any."""
    best_matching_type = _get_best_matching_type(python_value)
    converter = _CONVERTER_FOR_PYTHON_TYPE[best_matching_type]
    return converter.to_protobuf_any(python_value)


def _get_best_matching_type(python_value: object) -> str:
    underlying_parents = type(python_value).mro()  # This covers enum.IntEnum and similar

    container_type = None
    value_is_collection = _CONVERTIBLE_COLLECTION_TYPES.intersection(underlying_parents)
    if value_is_collection:
        # Assume Sized -- Generators not supported, callers must use list(), set(), ... as desired
        if not isinstance(python_value, Collection):
            raise TypeError()
        if len(python_value) == 0:
            underlying_parents = type(None).mro()
        else:
            # Assume homogenous -- collections of mixed-types not supported
            visitor = iter(python_value)
            first_value = next(visitor)
            underlying_parents = type(first_value).mro()
        container_type = Collection

    best_matching_type = None
    candidates = [parent.__name__ for parent in underlying_parents]
    for candidate in candidates:
        python_typename = f"{container_type.__name__}.{candidate}" if container_type else candidate
        if python_typename not in _SUPPORTED_PYTHON_TYPES:
            continue
        best_matching_type = python_typename
        break

    if not best_matching_type:
        payload_type = underlying_parents[0]
        raise TypeError(
            f"Unsupported type: ({container_type}, {payload_type}) with parents {underlying_parents}. Supported types are: {_SUPPORTED_PYTHON_TYPES}"
        )
    _logger.debug(f"Best matching type for '{repr(python_value)}' resolved to {best_matching_type}")
    return best_matching_type


def from_any(protobuf_any: any_pb2.Any) -> object:
    """Convert a protobuf Any to a Python object."""
    if not isinstance(protobuf_any, any_pb2.Any):
        raise ValueError(f"Unexpected type: {type(protobuf_any)}")

    underlying_typename = protobuf_any.TypeName()
    _logger.debug(f"Unpacking type '{underlying_typename}'")

    converter = _CONVERTER_FOR_GRPC_TYPE[underlying_typename]
    return converter.to_python(protobuf_any)
