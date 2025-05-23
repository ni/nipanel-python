from __future__ import annotations

from abc import ABC

import grpc
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool

from nipanel._panel_client import PanelClient


class PanelAccessor(ABC):
    """This class allows you to access values for a panel's controls."""

    _panel_client: PanelClient
    _panel_id: str

    __slots__ = ["_panel_client", "_panel_id"]

    def __init__(
        self,
        *,
        panel_id: str,
        provided_interface: str,
        service_class: str,
        discovery_client: DiscoveryClient | None = None,
        grpc_channel_pool: GrpcChannelPool | None = None,
        grpc_channel: grpc.Channel | None = None,
    ) -> None:
        """Initialize the accessor."""
        self._panel_client = PanelClient(
            provided_interface=provided_interface,
            service_class=service_class,
            discovery_client=discovery_client,
            grpc_channel_pool=grpc_channel_pool,
            grpc_channel=grpc_channel,
        )
        self._panel_id = panel_id

    @property
    def panel_id(self) -> str:
        """Read-only accessor for the panel ID."""
        return self._panel_id

    def get_value(self, value_id: str) -> object:
        """Get the value for a control on the panel.

        Args:
            value_id: The id of the value

        Returns:
            The value
        """
        return self._panel_client.get_value(self._panel_id, value_id)

    def set_value(self, value_id: str, value: object) -> None:
        """Set the value for a control on the panel.

        Args:
            value_id: The id of the value
            value: The value
        """
        self._panel_client.set_value(self._panel_id, value_id, value)
