from nipanel._panel import Panel


class StreamlitPanel(Panel):
    """This class allows you to connect to a Streamlit panel and specify values for its controls."""

    __slots__ = ()

    def __init__(self, streamlit_script_uri: str, panel_id: str) -> None:
        """Create a panel using a Streamlit script for the user interface.

        Args:
            streamlit_script_uri: The file path of the Streamlit script.
            panel_id: A unique identifier for the panel.

        Returns:
            A new StreamlitPanel instance.
        """
        super().__init__(streamlit_script_uri, panel_id)

    def _resolve_service_location(self) -> str:
        # TODO: AB#3095680 - resolve to the Streamlit PythonPanelService
        return ""
