"""The NI Panel."""

from nipanel._panel import Panel
from nipanel._streamlit_panel import StreamlitPanel
from nipanel._streamlit_panel_value_accessor import StreamlitPanelValueAccessor

__all__ = ["Panel", "StreamlitPanel", "StreamlitPanelValueAccessor"]

# Hide that it was defined in a helper file
Panel.__module__ = __name__
StreamlitPanel.__module__ = __name__
