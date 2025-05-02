from __future__ import annotations

from abc import ABC

import grpc
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool

from nipanel._panel_client import PanelClient


class Panel(ABC):
    """This class allows you to open a panel and specify values for its controls."""

    _panel_client: PanelClient
    _panel_id: str
    _panel_uri: str

    __slots__ = ["_panel_client", "_panel_id", "_panel_uri", "__weakref__"]

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
        self._panel_client = PanelClient(
            provided_interface=provided_interface,
            service_class=service_class,
            discovery_client=discovery_client,
            grpc_channel_pool=grpc_channel_pool,
            grpc_channel=grpc_channel,
        )
        self._panel_id = panel_id
        self._panel_uri = panel_uri

    @property
    def panel_id(self) -> str:
        """Read-only accessor for the panel ID."""
        return self._panel_id

    @property
    def panel_uri(self) -> str:
        """Read-only accessor for the panel URI."""
        return self._panel_uri

    def open_panel(self) -> None:
        """Open the panel."""
        self._panel_client.open_panel(self._panel_id, self._panel_uri)

    def get_value(self, value_id: str) -> object:
        """Get the value for a control on the panel.

        Args:
            value_id: The id of the value

        Returns:
            The value
        """
        # TODO: AB#3095681 - get the Any from _client.get_value and convert it to the correct type
        return "placeholder value"

    def set_value(self, value_id: str, value: object) -> None:
        """Set the value for a control on the panel.

        Args:
            value_id: The id of the value
            value: The value
        """
        # TODO: AB#3095681 - Convert the value to an Any and pass it to _client.set_value
        pass
