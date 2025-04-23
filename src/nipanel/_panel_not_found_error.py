class PanelNotFoundError(Exception):
    """Exception raised when a panel is not found."""

    def __init__(self, panel_id: str, panel_uri: str):
        """Initialize the exception with panel ID and URI."""
        super().__init__(f"Panel not found: {panel_id} - {panel_uri}")
        self.panel_id = panel_id
        self.panel_uri = panel_uri
