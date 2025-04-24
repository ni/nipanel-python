from nipanel._panel import Panel


class FakePanel(Panel):
    """This class allows you to connect to the FakePythonPanelService, for testing."""

    def __init__(self, port: int, panel_id: str, panel_uri: str) -> None:
        """Create a fake panel, for testing.

        Args:
            port: The port number for the gRPC server.
            panel_id: A unique identifier for the panel.
            panel_uri: The file path of the panel script.

        Returns:
            A new FakePanel instance.
        """
        super().__init__(panel_id, panel_uri)
        self.port = port

    def _get_channel_url(self) -> str:
        return f"localhost:{self.port}"
