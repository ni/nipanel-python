"""Streamlit UI components for NI Panel."""

from enum import Enum
from typing import TypeVar

import streamlit as st

from nipanel._panel_value_accessor import PanelValueAccessor

T = TypeVar("T", bound=Enum)


def enum_selectbox(panel: PanelValueAccessor, label: str, value: T, key: str) -> T:
    """Create a selectbox for an Enum.

    The selectbox will display the names of all the enum values, and when a value is selected,
    that value will be stored in the panel under the specified key.

    Args:
        panel: The panel
        label: Label to display for the selectbox
        value: The default enum value to select (also determines the specific enum type)
        key: Key to use for storing the enum value in the panel

    Returns:
        The selected enum value of the same specific enum subclass as the input value
    """
    enum_class = type(value)
    if not issubclass(enum_class, Enum):
        raise TypeError(f"Expected an Enum type, got {type(value)}")

    options = [(e.name, e.value) for e in enum_class]

    default_index = 0
    if value is not None:
        for i, (name, _) in enumerate(options):
            if name == value.name:
                default_index = i
                break

    box_tuple = st.selectbox(
        label,
        options=options,
        format_func=lambda x: x[0],
        index=default_index,
    )
    enum_value = enum_class[box_tuple[0]]
    panel.set_value(key, enum_value)
    return enum_value
