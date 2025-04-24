from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool

from nipanel._panel import Panel


class StreamlitPanel(Panel):
    """This class allows you to connect to a Streamlit panel and specify values for its controls."""

    PYTHON_PANEL_SERVICE = "ni.pythonpanel.v1.PythonPanelService"

    __slots__ = ()

    def __init__(self, panel_id: str, streamlit_script_uri: str) -> None:
        """Create a panel using a Streamlit script for the user interface.

        Args:
            panel_id: A unique identifier for the panel.
            streamlit_script_uri: The file path of the Streamlit script.

        Returns:
            A new StreamlitPanel instance.
        """
        super().__init__(panel_id, streamlit_script_uri)

    def _resolve_service_address(self) -> str:
        with GrpcChannelPool() as grpc_channel_pool:
            discovery_client = DiscoveryClient(grpc_channel_pool=grpc_channel_pool)
            service_location = discovery_client.resolve_service(self.PYTHON_PANEL_SERVICE)
            return service_location.insecure_address
