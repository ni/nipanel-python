"""The NI Panel."""

from nipanel._panel import Panel

__all__ = ["Panel"]

# Hide that it was defined in a helper file
Panel.__module__ = __name__
