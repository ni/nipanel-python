from pathlib import Path
from typing import cast

import streamlit as st

from nipanel._convert import is_supported_type
from nipanel._panel_value_accessor import PanelValueAccessor
from nipanel._streamlit_panel import StreamlitPanel
from nipanel.streamlit_refresh import initialize_refresh_component

PANEL_ACCESSOR_KEY = "StreamlitPanelValueAccessor"


def create_streamlit_panel(streamlit_script_path: Path, panel_id: str = "") -> StreamlitPanel:
    """Create a Streamlit panel with the specified script path.

    This function initializes a Streamlit panel using the provided script path. By default, it
    derives the panel ID from the script's path, which it expects to be a valid Streamlit script.
    For example, if the value for streamlit_script_path is "c:/example/some_example.py", then the
    panel's ID becomes "some_example". Alternatively, you can specify a custom panel_id.

    Use this function when you want to create a new panel instance to use in a Streamlit
    application. Do not call this function from within a Streamlit script.

    Args:
        streamlit_script_path: The file path of the Streamlit script to be used for the panel.
        panel_id: Optional custom panel ID. If not provided, it will be derived from the script
            path.

    Returns:
        A StreamlitPanel instance initialized with the given panel ID.
    """
    if st.get_option("server.baseUrlPath") != "":
        raise RuntimeError(
            "nipanel.create_panel() should not be called from a Streamlit script. Call nipanel.get_panel_accessor() instead."
        )
    if not isinstance(streamlit_script_path, Path):
        raise TypeError("The provided script path must be a pathlib.Path instance.")

    if streamlit_script_path.suffix != ".py":
        raise ValueError(
            "The provided script path must be a valid Streamlit script ending with '.py'."
        )

    if not panel_id:
        panel_id = streamlit_script_path.stem

    return StreamlitPanel(panel_id, streamlit_script_path)


def get_streamlit_panel_accessor() -> PanelValueAccessor:
    """Initialize and return the Streamlit panel value accessor.

    This function retrieves the Streamlit panel value accessor for the current Streamlit script.
    This function should only be called from within a Streamlit script. The accessor will be cached
    in the Streamlit session state to ensure that it is reused across reruns of the script.

    Returns:
        A PanelValueAccessor instance for the current panel.
    """
    if st.get_option("server.baseUrlPath") == "":
        raise RuntimeError(
            "nipanel.get_panel_accessor() should only be called from a Streamlit script. Call nipanel.create_panel() instead."
        )

    if PANEL_ACCESSOR_KEY not in st.session_state:
        st.session_state[PANEL_ACCESSOR_KEY] = _initialize_panel_from_base_path()

    panel = cast(PanelValueAccessor, st.session_state[PANEL_ACCESSOR_KEY])
    _sync_session_state(panel)
    refresh_component = initialize_refresh_component(panel.panel_id)
    refresh_component()
    return panel


def _initialize_panel_from_base_path() -> PanelValueAccessor:
    """Validate and parse the Streamlit base URL path and return a PanelValueAccessor."""
    base_url_path = st.get_option("server.baseUrlPath")
    if not base_url_path.startswith("/"):
        raise ValueError("Invalid or missing Streamlit server.baseUrlPath option.")
    panel_id = base_url_path.split("/")[-1]
    if not panel_id:
        raise ValueError(f"Panel ID is empty in baseUrlPath: '{base_url_path}'")
    return PanelValueAccessor(
        panel_id=panel_id,
        notify_on_set_value=False,
    )


def _sync_session_state(panel: PanelValueAccessor) -> None:
    """Automatically read keyed control values from the session state."""
    for key in st.session_state.keys():
        value = st.session_state[key]
        if is_supported_type(value):
            panel.set_value_if_changed(str(key), value)
