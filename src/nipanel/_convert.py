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
from nipanel.converters.protobuf_types import (
    Double2DArrayConverter,
    DoubleAnalogWaveformConverter,
    ScalarConverter,
)

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
    Double2DArrayConverter(),
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

    container_types = []
    value_is_collection = any(_CONVERTIBLE_COLLECTION_TYPES.intersection(underlying_parents))
    # Variable to use when traversing down through collection types.
    working_python_value = python_value
    while value_is_collection:
        # Assume Sized -- Generators not supported, callers must use list(), set(), ... as desired
        if not isinstance(working_python_value, Collection):
            raise TypeError()
        if len(working_python_value) == 0:
            underlying_parents = type(None).mro()
            value_is_collection = False
        else:
            # Assume homogenous -- collections of mixed-types not supported
            visitor = iter(working_python_value)

            # Store off the first element. If it's a container, we'll need it in the next while
            # loop iteration.
            working_python_value = next(visitor)
            underlying_parents = type(working_python_value).mro()

            # If this element is a collection, we want to continue traversing. Once we find a
            # non-collection, underlying_parents will refer to the candidates for the non-
            # collection type.
            value_is_collection = any(
                _CONVERTIBLE_COLLECTION_TYPES.intersection(underlying_parents)
            )
        container_types.append(Collection.__name__)

    best_matching_type = None
    candidates = [parent.__name__ for parent in underlying_parents]
    for candidate in candidates:
        containers_str = ".".join(container_types)
        python_typename = f"{containers_str}.{candidate}" if containers_str else candidate
        if python_typename not in _SUPPORTED_PYTHON_TYPES:
            continue
        best_matching_type = python_typename
        break

    if not best_matching_type:
        payload_type = underlying_parents[0]
        raise TypeError(
            f"Unsupported type: ({container_types}, {payload_type}) with parents "
            f"{underlying_parents}. Supported types are: {_SUPPORTED_PYTHON_TYPES}"
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
