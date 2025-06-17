""" Panel refresh component for Streamlit. """

import streamlit.components.v1 as components
from nipanel._streamlit_constants import STREAMLIT_REFRESH_COMPONENT_URL

def add_refresh_component(panel_id):

    refresh_component = components.declare_component(
        "panelRefreshComponent",
        url=f"{STREAMLIT_REFRESH_COMPONENT_URL}/{panel_id}",
        key=f"panel_refresh_{panel_id}",
    )

    return refresh_component
