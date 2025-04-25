from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from types import TracebackType
from typing import TYPE_CHECKING, Optional, Type

from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient

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

    def __init__(self, panel_id: str, panel_uri: str) -> None:
        """Initialize the panel."""
        self._panel_client = PanelClient(self._resolve_service_address)
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
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> Optional[bool]:
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

    @abstractmethod
    def _resolve_service_address(self, discovery_client: DiscoveryClient) -> str:
        """Resolve the service address for the panel."""
        raise NotImplementedError
