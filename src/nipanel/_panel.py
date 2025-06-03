from __future__ import annotations

from abc import ABC
from types import TracebackType

import grpc
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool
from typing_extensions import Self

from nipanel._panel_value_accessor import PanelValueAccessor


class Panel(PanelValueAccessor, ABC):
    """This class allows you to open a panel and specify values for its controls."""

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

    def __enter__(self) -> Self:
        """Enter the runtime context related to this object."""
        self.open_panel()
        return self

    def __exit__(
        self,
        exctype: type[BaseException] | None,
        excinst: BaseException | None,
        exctb: TracebackType | None,
    ) -> bool | None:
        """Exit the runtime context related to this object."""
        self.close_panel(reset=False)
        return None

    def open_panel(self) -> None:
        """Open the panel."""
        self._panel_client.open_panel(self._panel_id, self._panel_uri)

    def close_panel(self, reset: bool) -> None:
        """Close the panel.

        Args:
            reset: Whether to reset all storage associated with the panel.
        """
        self._panel_client.close_panel(self._panel_id, reset=reset)
