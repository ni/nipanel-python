"""The NI Panel."""

from nipanel._streamlit_panel import StreamlitPanel

__all__ = ["StreamlitPanel"]

# Hide that it was defined in a helper file
StreamlitPanel.__module__ = __name__
