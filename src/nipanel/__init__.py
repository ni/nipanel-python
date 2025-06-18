"""The NI Panel."""

from importlib.metadata import version

from nipanel._panel import Panel
from nipanel._streamlit_panel import StreamlitPanel
from nipanel._streamlit_panel_initializer import initialize_panel
from nipanel._streamlit_panel_value_accessor import StreamlitPanelValueAccessor

__all__ = ["Panel", "StreamlitPanel", "StreamlitPanelValueAccessor", "initialize_panel"]

# Hide that it was defined in a helper file
Panel.__module__ = __name__
StreamlitPanel.__module__ = __name__

__version__ = version(__name__)
