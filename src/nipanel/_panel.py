from __future__ import annotations

from abc import ABC

import grpc
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool

from nipanel._panel_value_accessor import PanelValueAccessor


class Panel(PanelValueAccessor, ABC):
    """This class allows you to open a panel and specify values for its controls."""

    __slots__ = ["_panel_script_path", "_panel_url"]

    def __init__(
        self,
        *,
        panel_id: str,
        panel_script_path: str,
        provided_interface: str,
        service_class: str,
        discovery_client: DiscoveryClient | None = None,
        grpc_channel_pool: GrpcChannelPool | None = None,
        grpc_channel: grpc.Channel | None = None,
    ) -> None:
        """Initialize the panel."""
        super().__init__(
            panel_id=panel_id,
            provided_interface=provided_interface,
            service_class=service_class,
            discovery_client=discovery_client,
            grpc_channel_pool=grpc_channel_pool,
            grpc_channel=grpc_channel,
        )
        self._panel_script_path = panel_script_path
        self._panel_url = self._panel_client.start_panel(panel_id, panel_script_path)

    @property
    def panel_script_path(self) -> str:
        """Read-only accessor for the panel script path."""
        return self._panel_script_path

    @property
    def panel_url(self) -> str:
        """Read-only accessor for the panel URL."""
        return self._panel_url
