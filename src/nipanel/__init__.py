"""The NI Panel."""

from importlib.metadata import version

from nipanel._panel import Panel
from nipanel.controls._enum_selectbox import enum_selectbox
from nipanel._streamlit_panel import StreamlitPanel
from nipanel._streamlit_panel_initializer import create_panel, get_panel_accessor
from nipanel._streamlit_panel_value_accessor import StreamlitPanelValueAccessor

__all__ = [
    "create_panel",
    "enum_selectbox",
    "get_panel_accessor",
    "Panel",
    "StreamlitPanel",
    "StreamlitPanelValueAccessor",
]

# Hide that it was defined in a helper file
Panel.__module__ = __name__
StreamlitPanel.__module__ = __name__

__version__ = version(__name__)
"""nipanel version string."""
