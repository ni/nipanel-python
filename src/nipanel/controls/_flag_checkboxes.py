"""A set of checkboxes for selecting Flag enum values."""

from enum import Flag
from typing import TypeVar, Callable

import streamlit as st

from nipanel._streamlit_panel_value_accessor import StreamlitPanelValueAccessor

T = TypeVar("T", bound=Flag)


def flag_checkboxes(
    panel: StreamlitPanelValueAccessor,
    label: str,
    value: T,
    key: str,
    disabled: bool = False,
    label_formatter: Callable[[Flag], str] = lambda x: str(x.name),
) -> T:
    """Create a set of checkboxes for a Flag enum.

    This will display a checkbox for each individual flag value in the enum. When checkboxes
    are selected or deselected, the combined Flag value will be stored in the panel under
    the specified key.

    Args:
        panel: The panel
        label: Label to display above the checkboxes
        value: The default Flag enum value (also determines the specific Flag enum type)
        key: Key to use for storing the Flag value in the panel
        disabled: Whether the checkboxes should be disabled
        label_formatter: Function that formats the flag to a string for display. Default
                         uses flag.name.

    Returns:
        The selected Flag enum value with all selected flags combined
    """
    flag_type = type(value)
    if not issubclass(flag_type, Flag):
        raise TypeError(f"Expected a Flag enum type, got {type(value)}")

    st.markdown(f"<small>{label}:</small>", unsafe_allow_html=True)

    # Get all individual flag values (skip composite values and zero value)
    flag_values = [
        flag for flag in flag_type if flag.value & (flag.value - 1) == 0 and flag.value != 0
    ]

    # Create a container for flag checkboxes
    flag_container = st.container(border=True)
    selected_flags = flag_type(0)  # Start with no flags

    # If default value is set, use it as the initial state
    if value:
        selected_flags = value

    # Create a checkbox for each flag
    for flag in flag_values:
        is_selected = bool(selected_flags & flag)
        if flag_container.checkbox(
            label=label_formatter(flag),
            value=is_selected,
            key=f"{key}_{flag.name}",
            disabled=disabled,
        ):
            selected_flags |= flag
        else:
            selected_flags &= ~flag

    # Store the selected flags in the panel
    panel.set_value_if_changed(key, selected_flags)
    return selected_flags
