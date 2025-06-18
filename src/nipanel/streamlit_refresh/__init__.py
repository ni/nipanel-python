"""Initializes a refresh component for Streamlit."""

from typing import Any

import streamlit.components.v1 as components

from nipanel._streamlit_constants import STREAMLIT_REFRESH_COMPONENT_URL


def initialize_refresh_component(panel_id: str) -> Any:
    """Initialize a refresh component to the Streamlit app."""
    _refresh_component_func = components.declare_component(
        "panelRefreshComponent",
        url=f"{STREAMLIT_REFRESH_COMPONENT_URL}/{panel_id}",
    )

    return _refresh_component_func
