from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from types import TracebackType
from typing import TYPE_CHECKING, Optional, Type

from grpc import RpcError, StatusCode, insecure_channel
from ni.pythonpanel.v1.python_panel_service_pb2 import ConnectRequest, DisconnectRequest
from ni.pythonpanel.v1.python_panel_service_pb2_grpc import PythonPanelServiceStub

from nipanel._panel_not_found_error import PanelNotFoundError

if TYPE_CHECKING:
    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self


class Panel(ABC):
    """This class allows you to connect to a panel and specify values for its controls."""

    _stub: PythonPanelServiceStub | None
    _panel_id: str
    _panel_uri: str

    __slots__ = ["_stub", "_panel_id", "_panel_uri", "__weakref__"]

    def __init__(self, panel_id: str, panel_uri: str) -> None:
        """Initialize the panel."""
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
        # TODO: use the channel pool
        channel = insecure_channel(self._resolve_service_address())
        self._stub = PythonPanelServiceStub(channel)
        connect_request = ConnectRequest(panel_id=self._panel_id, panel_uri=self._panel_uri)

        try:
            self._stub.Connect(connect_request)
        except RpcError as e:
            if e.code() == StatusCode.NOT_FOUND:
                raise PanelNotFoundError(self._panel_id, self._panel_uri) from e
            else:
                raise

    def disconnect(self) -> None:
        """Disconnect from the panel (does not close the panel)."""
        disconnect_request = DisconnectRequest(panel_id=self._panel_id)

        if self._stub is None:
            raise RuntimeError("connect() must be called before disconnect()")

        try:
            self._stub.Disconnect(disconnect_request)
        except RpcError as e:
            if e.code() == StatusCode.NOT_FOUND:
                raise PanelNotFoundError(self._panel_id, self._panel_uri) from e
            else:
                raise

        self._stub = None
        # TODO: channel pool cleanup?

    def get_value(self, value_id: str) -> object:
        """Get the value for a control on the panel.

        Args:
            value_id: The id of the value

        Returns:
            The value
        """
        # TODO: AB#3095681 - get the Any from _stub.GetValue and convert it to the correct type
        return "placeholder value"

    def set_value(self, value_id: str, value: object) -> None:
        """Set the value for a control on the panel.

        Args:
            value_id: The id of the value
            value: The value
        """
        # TODO: AB#3095681 - Convert the value to an Any and pass it to _stub.SetValue
        pass

    @abstractmethod
    def _resolve_service_address(self) -> str:
        """Resolve the service location for the panel."""
        raise NotImplementedError
