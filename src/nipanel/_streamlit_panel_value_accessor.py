from __future__ import annotations

from typing import final

import grpc
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool

from nipanel._panel_value_accessor import PanelValueAccessor
from nipanel._streamlit_constants import STREAMLIT_PYTHON_PANEL_SERVICE


@final
class StreamlitPanelValueAccessor(PanelValueAccessor):
    """This class provides access to values for a Streamlit panel's controls.

    This class should only be used within a Streamlit script.
    """

    def __init__(
        self,
        panel_id: str,
        *,
        discovery_client: DiscoveryClient | None = None,
        grpc_channel_pool: GrpcChannelPool | None = None,
        grpc_channel: grpc.Channel | None = None,
    ) -> None:
        """Create an accessor for a Streamlit panel.

        Args:
            panel_id: A unique identifier for the panel.
            grpc_channel: An optional gRPC channel to use for communication with the panel service.

        Returns:
            A new StreamlitPanelAccessor instance.
        """
        super().__init__(
            panel_id=panel_id,
            provided_interface=STREAMLIT_PYTHON_PANEL_SERVICE,
            service_class=STREAMLIT_PYTHON_PANEL_SERVICE,
            notify_on_set_value=False,
            discovery_client=discovery_client,
            grpc_channel_pool=grpc_channel_pool,
            grpc_channel=grpc_channel,
        )
