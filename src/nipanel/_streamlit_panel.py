from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool

from nipanel._panel import Panel


class StreamlitPanel(Panel):
    """This class allows you to connect to a Streamlit panel and specify values for its controls."""

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

    def _get_channel_url(self) -> str:
        with GrpcChannelPool() as grpc_channel_pool:
            discovery_client = DiscoveryClient(grpc_channel_pool=grpc_channel_pool)
            service_location = discovery_client.resolve_service(
                "ni.pythonpanel.v1.PythonPanelService"
            )
        return service_location.insecure_address
