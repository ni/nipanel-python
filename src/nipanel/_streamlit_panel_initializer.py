from typing import cast

import streamlit as st
from nipanel.streamlit_components.refresh import initialize_refresh_component

from nipanel._streamlit_panel_value_accessor import StreamlitPanelValueAccessor

PANEL_ACCESSOR_KEY = "StreamlitPanelValueAccessor"


def initialize_panel() -> StreamlitPanelValueAccessor:
    """Initialize and return the Streamlit panel value accessor.

    This function retrieves the Streamlit panel value accessor for the current Streamlit script.
    It is typically used within a Streamlit script to access and manipulate panel values.
    The accessor will be cached in the Streamlit session state to ensure that it is reused across
    reruns of the script.

    Returns:
        A StreamlitPanelValueAccessor instance for the current panel.
    """
    if PANEL_ACCESSOR_KEY not in st.session_state:
        st.session_state[PANEL_ACCESSOR_KEY] = _initialize_panel_from_base_path()

    panel = cast(StreamlitPanelValueAccessor, st.session_state[PANEL_ACCESSOR_KEY])
    refresh_component = initialize_refresh_component(panel.panel_id)
    refresh_component()
    return panel


def _initialize_panel_from_base_path() -> StreamlitPanelValueAccessor:
    """Validate and parse the Streamlit base URL path and return a StreamlitPanelValueAccessor."""
    base_url_path = st.get_option("server.baseUrlPath")
    if not base_url_path.startswith("/"):
        raise ValueError("Invalid or missing Streamlit server.baseUrlPath option.")
    panel_id = base_url_path.split("/")[-1]
    if not panel_id:
        raise ValueError(f"Panel ID is empty in baseUrlPath: '{base_url_path}'")
    return StreamlitPanelValueAccessor(panel_id)
