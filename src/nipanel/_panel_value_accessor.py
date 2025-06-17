from __future__ import annotations

from abc import ABC
from typing import TypeVar, overload, cast

import grpc
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool

from nipanel._panel_client import PanelClient

_T = TypeVar("_T")


class PanelValueAccessor(ABC):
    """This class allows you to access values for a panel's controls."""

    __slots__ = ["_panel_client", "_panel_id", "_notify_on_set_value", "__weakref__"]

    def __init__(
        self,
        *,
        panel_id: str,
        provided_interface: str,
        service_class: str,
        notify_on_set_value: bool = True,
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
        self._notify_on_set_value = notify_on_set_value

    @property
    def panel_id(self) -> str:
        """Read-only accessor for the panel ID."""
        return self._panel_id

    @overload
    def get_value(self, value_id: str) -> object: ...

    @overload
    def get_value(self, value_id: str, default_value: _T) -> _T: ...

    def get_value(self, value_id: str, default_value: _T | None = None) -> _T:
        """Get the value for a control on the panel with an optional default value.

        Args:
            value_id: The id of the value
            default_value: The default value to return if the value is not set

        Returns:
            The value, or the default value if not set
        """
        try:
            value = cast(_T, self._panel_client.get_value(self._panel_id, value_id))
            if default_value is not None and not isinstance(value, type(default_value)):
                raise TypeError("Value type does not match default value type.")
            return value

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND and default_value is not None:
                return default_value
            else:
                raise e

    def set_value(self, value_id: str, value: object) -> None:
        """Set the value for a control on the panel.

        Args:
            value_id: The id of the value
            value: The value
        """
        self._panel_client.set_value(
            self._panel_id, value_id, value, notify=self._notify_on_set_value
        )
