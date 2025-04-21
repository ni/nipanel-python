"""NI Panel."""

import uuid
from types import TracebackType
from typing import Optional, Type


class NiPanel:
    """This class allows you to access controls on the panel."""

    def __init__(self) -> None:
        """Initialize the NiPanel instance."""
        self._stub = None  # will be a PythonPanelServiceStub
        self.panel_uri = ""
        self.panel_id = ""

    def __enter__(self) -> "NiPanel":
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

    @classmethod
    def streamlit_panel(cls, streamlit_script_path: str) -> "NiPanel":
        """Create a panel using a streamlit script for the user interface.

        Args:
            streamlit_script_path: The file path of the streamlit script

        Returns:
            NiPanel: A new panel associated with the streamlit script
        """
        panel = cls()
        panel.panel_uri = streamlit_script_path
        panel.panel_id = str(uuid.uuid4())
        return panel

    def connect(self) -> None:
        """Connect to the panel and open it."""
        # TODO: AB#3095680 - Use gRPC pool management, create the _stub, and call _stub.Connect
        pass

    def disconnect(self) -> None:
        """Disconnect from the panel (does not close the panel)."""
        # TODO: AB#3095680 - Use gRPC pool management, call _stub.Disconnect
        pass

    def get_value(self, value_id: str) -> object:
        """Get the value for a control on the panel.

        Args:
            value_id: The id of the value

        Returns:
            object: The value
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
