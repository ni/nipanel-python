"""Initializes a refresh component for Streamlit."""

from streamlit.components.v1 import declare_component
from streamlit.components.v1.custom_component import CustomComponent


def initialize_refresh_component(panel_id: str) -> CustomComponent:
    """Initialize a refresh component to the Streamlit app."""
    proxy_url = "TODO"
    _refresh_component_func = declare_component(
        "panelRefreshComponent",
        url=f"http://{proxy_url}/panel-service/refresh/{panel_id}",
    )

    return _refresh_component_func
