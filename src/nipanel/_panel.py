from __future__ import annotations

import sys
import uuid
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Type, TYPE_CHECKING

from ni.pythonpanel.v1.python_panel_service_pb2_grpc import PythonPanelServiceStub

if TYPE_CHECKING:
    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self


class Panel(ABC):
    """This class allows you to connect to a panel and specify values for its controls."""

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

    @abstractmethod
    def connect(self) -> None:
        """Connect to the panel and open it."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the panel (does not close the panel)."""
        pass

    @abstractmethod
    def get_value(self, value_id: str) -> object:
        """Get the value for a control on the panel.

        Args:
            value_id: The id of the value

        Returns:
            The value
        """
        pass

    @abstractmethod
    def set_value(self, value_id: str, value: object) -> None:
        """Set the value for a control on the panel.

        Args:
            value_id: The id of the value
            value: The value
        """
        pass

    @classmethod
    def streamlit_panel(cls, streamlit_script_path: str) -> Panel:
        """Create a panel using a streamlit script for the user interface.

        Args:
            streamlit_script_path: The file path of the Streamlit script.

        Returns:
            A new StreamlitPanel instance.
        """
        return _StreamlitPanel(streamlit_script_path)


class _StreamlitPanel(Panel):

    _stub: PythonPanelServiceStub | None
    _streamlit_script_uri: str
    _panel_id: str

    __slots__ = ["_stub", "_streamlit_script_uri", "_panel_id"]

    def __init__(self, streamlit_script_uri: str):
        self._streamlit_script_uri = streamlit_script_uri
        self._panel_id = str(uuid.uuid4())
        self._stub = None  # Initialize the gRPC stub

    def connect(self) -> None:
        # TODO: AB#3095680 - Use gRPC pool management, create the _stub, and call _stub.Connect
        pass

    def disconnect(self) -> None:
        # TODO: AB#3095680 - Use gRPC pool management, call _stub.Disconnect
        pass

    def get_value(self, value_id: str) -> object:
        # TODO: AB#3095681 - get the Any from _stub.GetValue and convert it to the correct type
        return "placeholder value"

    def set_value(self, value_id: str, value: object) -> None:
        # TODO: AB#3095681 - Convert the value to an Any and pass it to _stub.SetValue
        pass
