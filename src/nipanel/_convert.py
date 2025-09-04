"""Functions to convert between different data formats."""

from __future__ import annotations

import enum
import logging
from collections.abc import Collection
from typing import Any, Iterable

from google.protobuf import any_pb2
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform

from nipanel.converters import Converter
from nipanel.converters.builtin import (
    BoolConverter,
    BytesConverter,
    DTDateTimeConverter,
    DTTimeDeltaConverter,
    FloatConverter,
    IntConverter,
    StrConverter,
)
from nipanel.converters.protobuf_types import (
    BTDateTimeConverter,
    BTTimeDeltaConverter,
    BoolCollectionConverter,
    BytesCollectionConverter,
    DigitalWaveformConverter,
    Double2DArrayConverter,
    DoubleAnalogWaveformConverter,
    DoubleComplexWaveformConverter,
    DoubleSpectrumConverter,
    FloatCollectionConverter,
    HTDateTimeConverter,
    HTTimeDeltaConverter,
    Int16AnalogWaveformConverter,
    Int16ComplexWaveformConverter,
    IntCollectionConverter,
    ScalarConverter,
    StrCollectionConverter,
    VectorConverter,
)

_logger = logging.getLogger(__name__)

# FFV -- consider adding a RegisterConverter mechanism
_CONVERTIBLE_TYPES: list[Converter[Any, Any]] = [
    # Built-in Types
    BoolConverter(),
    BytesConverter(),
    FloatConverter(),
    IntConverter(),
    StrConverter(),
    DTDateTimeConverter(),
    DTTimeDeltaConverter(),
    # Protobuf Types
    BTDateTimeConverter(),
    BTTimeDeltaConverter(),
    BoolCollectionConverter(),
    BytesCollectionConverter(),
    DigitalWaveformConverter(),
    Double2DArrayConverter(),
    DoubleAnalogWaveformConverter(),
    DoubleComplexWaveformConverter(),
    DoubleSpectrumConverter(),
    FloatCollectionConverter(),
    HTDateTimeConverter(),
    HTTimeDeltaConverter(),
    Int16AnalogWaveformConverter(),
    Int16ComplexWaveformConverter(),
    IntCollectionConverter(),
    StrCollectionConverter(),
    ScalarConverter(),
    VectorConverter(),
]

_CONVERTER_FOR_PYTHON_TYPE = {entry.python_typename: entry for entry in _CONVERTIBLE_TYPES}
_CONVERTER_FOR_GRPC_TYPE = {entry.protobuf_typename: entry for entry in _CONVERTIBLE_TYPES}
_SUPPORTED_PYTHON_TYPES = _CONVERTER_FOR_PYTHON_TYPE.keys()

_SKIPPED_COLLECTIONS = (
    str,  # Handled by StrConverter
    bytes,  # Handled by BytesConverter
    dict,  # Unsupported data type
    enum.Enum,  # Handled by IntConverter
    Vector,  # Handled by VectorConverter
)


def to_any(python_value: object) -> any_pb2.Any:
    """Convert a Python object to a protobuf Any."""
    best_matching_type = _get_best_matching_type(python_value)
    converter = _CONVERTER_FOR_PYTHON_TYPE[best_matching_type]
    return converter.to_protobuf_any(python_value)


def _get_best_matching_type(python_value: object) -> str:
    underlying_parents = type(python_value).mro()  # This covers enum.IntEnum and similar
    additional_info_string = _get_additional_type_info_string(python_value)

    container_types = []
    value_is_collection = _is_collection_for_convert(python_value)
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
            value_is_collection = _is_collection_for_convert(working_python_value)
        container_types.append(Collection)

    best_matching_type = None
    candidates = _get_candidate_strings(underlying_parents)
    for candidate in candidates:
        python_typename = _create_python_typename(
            candidate, container_types, additional_info_string
        )
        if python_typename not in _SUPPORTED_PYTHON_TYPES:
            continue
        best_matching_type = python_typename
        break

    if not best_matching_type:
        payload_type = underlying_parents[0]
        raise TypeError(
            f"Unsupported type: ({container_types}, {payload_type}) with parents "
            f"{underlying_parents}.\n\nSupported types are: {_SUPPORTED_PYTHON_TYPES}"
            f"\n\nAdditional type info: {additional_info_string}"
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


def is_supported_type(value: object) -> bool:
    """Check if a given Python value can be converted to protobuf Any."""
    try:
        _get_best_matching_type(value)
        return True
    except TypeError:
        return False


def _get_candidate_strings(candidates: Iterable[type]) -> list[str]:
    candidate_names = []
    for candidate in candidates:
        candidate_names.append(f"{candidate.__module__}.{candidate.__name__}")
    return candidate_names


def _create_python_typename(
    candidate_name: str, container_types: Iterable[type], additional_info: str
) -> str:
    name = candidate_name
    if additional_info:
        name = f"{name}[{additional_info}]"
    for container_type in container_types:
        name = f"{container_type.__module__}.{container_type.__name__}[{name}]"
    return name


def _get_additional_type_info_string(python_value: object) -> str:
    if isinstance(python_value, AnalogWaveform):
        return str(python_value.dtype)
    elif isinstance(python_value, ComplexWaveform):
        return str(python_value.dtype)
    else:
        return ""


def _is_collection_for_convert(python_value: object) -> bool:
    return isinstance(python_value, Collection) and not isinstance(
        python_value, _SKIPPED_COLLECTIONS
    )
