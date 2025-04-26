from __future__ import annotations

import sys
from abc import ABC
from types import TracebackType
from typing import TYPE_CHECKING

import grpc
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool

from nipanel._panel_client import PanelClient

if TYPE_CHECKING:
    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self


class Panel(ABC):
    """This class allows you to connect to a panel and specify values for its controls."""

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

    def __enter__(self) -> Self:
        """Enter the runtime context related to this object."""
        self.connect()
        return self

    def __exit__(
        self,
        exctype: type[BaseException] | None,
        excinst: BaseException | None,
        exctb: TracebackType | None,
    ) -> bool | None:
        """Exit the runtime context related to this object."""
        self.disconnect()
        return None

    def connect(self) -> None:
        """Connect to the panel and open it."""
        self._panel_client.connect(self._panel_id, self._panel_uri)

    def disconnect(self) -> None:
        """Disconnect from the panel (does not close the panel)."""
        self._panel_client.disconnect(self._panel_id)

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
