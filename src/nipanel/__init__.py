"""The NI Panel."""

from importlib.metadata import version

from nipanel._panel_value_accessor import PanelValueAccessor
from nipanel._streamlit_panel import StreamlitPanel
from nipanel._streamlit_panel_initializer import (
    create_streamlit_panel,
    get_streamlit_panel_accessor,
)

__all__ = [
    "create_streamlit_panel",
    "get_streamlit_panel_accessor",
    "PanelValueAccessor",
    "StreamlitPanel",
]

# Hide that it was defined in a helper file
PanelValueAccessor.__module__ = __name__
StreamlitPanel.__module__ = __name__

__version__ = version(__name__)
"""nipanel version string."""
