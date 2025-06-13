from typing import cast

import streamlit as st

from nipanel._streamlit_panel_value_accessor import StreamlitPanelValueAccessor


def initialize_panel() -> StreamlitPanelValueAccessor:
    """Initialize and return the Streamlit panel value accessor.

    This function retrieves the Streamlit panel value accessor for the current Streamlit script.
    It is typically used within a Streamlit script to access and manipulate panel values.
    The accessor will be cached in the Streamlit session state to ensure that it is reused across
    reruns of the script.

    Returns:
        A StreamlitPanelValueAccessor instance for the current panel.
    """
    if "StreamlitPanelValueAccessor" not in st.session_state:
        # streamlit is launched with something like --server.baseUrlPath=/my_panel,
        # which allows us to get the panel ID from the URL.
        panel_id = st.get_option("server.baseUrlPath").split("/")[-1]
        st.session_state["StreamlitPanelValueAccessor"] = StreamlitPanelValueAccessor(panel_id)

    return cast(StreamlitPanelValueAccessor, st.session_state["StreamlitPanelValueAccessor"])
