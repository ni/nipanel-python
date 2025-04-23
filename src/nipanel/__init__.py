"""The NI Panel."""

from nipanel._panel import Panel
from nipanel._streamlit_panel import StreamlitPanel

__all__ = ["Panel", "StreamlitPanel"]

# Hide that it was defined in a helper file
Panel.__module__ = __name__
StreamlitPanel.__module__ = __name__
