from __future__ import annotations

from abc import ABC

import grpc
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool

from nipanel._panel_value_accessor import PanelValueAccessor


class Panel(PanelValueAccessor, ABC):
    """This class allows you to open a panel and specify values for its controls."""

    _panel_uri: str

    __slots__ = ["_panel_uri"]

    def __init__(
        self,
        *,
        panel_id: str,
        panel_uri: str,
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
        self._panel_uri = panel_uri

    @property
    def panel_uri(self) -> str:
        """Read-only accessor for the panel URI."""
        return self._panel_uri

    def open_panel(self) -> None:
        """Open the panel."""
        self._panel_client.open_panel(self._panel_id, self._panel_uri)
