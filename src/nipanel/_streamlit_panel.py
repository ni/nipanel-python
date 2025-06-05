from __future__ import annotations

from typing import final

import grpc
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool

from nipanel._panel import Panel
from nipanel._streamlit_constants import STREAMLIT_PYTHON_PANEL_SERVICE


@final
class StreamlitPanel(Panel):
    """This class allows you to open a Streamlit panel and specify values for its controls."""

    def __init__(
        self,
        panel_id: str,
        streamlit_script_path: str,
        *,
        discovery_client: DiscoveryClient | None = None,
        grpc_channel_pool: GrpcChannelPool | None = None,
        grpc_channel: grpc.Channel | None = None,
    ) -> None:
        """Create a panel using a Streamlit script for the user interface.

        Args:
            panel_id: A unique identifier for the panel.
            streamlit_script_path: The file path of the Streamlit script.
            grpc_channel: An optional gRPC channel to use for communication with the panel service.

        Returns:
            A new StreamlitPanel instance.
        """
        super().__init__(
            panel_id=panel_id,
            panel_script_path=streamlit_script_path,
            provided_interface=STREAMLIT_PYTHON_PANEL_SERVICE,
            service_class=STREAMLIT_PYTHON_PANEL_SERVICE,
            discovery_client=discovery_client,
            grpc_channel_pool=grpc_channel_pool,
            grpc_channel=grpc_channel,
        )
