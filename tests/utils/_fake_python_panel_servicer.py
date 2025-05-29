from typing import Any

import grpc
from ni.pythonpanel.v1.python_panel_service_pb2 import (
    OpenPanelRequest,
    OpenPanelResponse,
    ClosePanelRequest,
    ClosePanelResponse,
    EnumeratePanelsRequest,
    EnumeratePanelsResponse,
    GetValueRequest,
    GetValueResponse,
    SetValueRequest,
    SetValueResponse,
)
from ni.pythonpanel.v1.python_panel_service_pb2_grpc import PythonPanelServiceServicer


class FakePythonPanelServicer(PythonPanelServiceServicer):
    """Fake implementation of the PythonPanelServicer for testing."""

    def __init__(self) -> None:
        """Initialize the fake PythonPanelServicer."""
        self._values: dict[str, Any] = {}
        self._panel_ids: list[str] = []
        self._fail_next_open_panel = False

    def OpenPanel(self, request: OpenPanelRequest, context: Any) -> OpenPanelResponse:  # noqa: N802
        """Trivial implementation for testing."""
        if self._fail_next_open_panel:
            self._fail_next_open_panel = False
            context.abort(grpc.StatusCode.UNAVAILABLE, "Simulated failure")
        self._panel_ids.append(request.panel_id)
        return OpenPanelResponse()

    def ClosePanel(  # noqa: N802
        self, request: ClosePanelRequest, context: Any
    ) -> ClosePanelResponse:
        """Trivial implementation for testing."""
        if request.reset:
            self._panel_ids.remove(request.panel_id)
            self._values.clear()
        return ClosePanelResponse()

    def EnumeratePanels(  # noqa: N802
        self, request: EnumeratePanelsRequest, context: Any
    ) -> EnumeratePanelsResponse:
        """Trivial implementation for testing."""
        return EnumeratePanelsResponse(panel_ids=self._panel_ids)

    def GetValue(self, request: GetValueRequest, context: Any) -> GetValueResponse:  # noqa: N802
        """Trivial implementation for testing."""
        value = self._values[request.value_id]
        return GetValueResponse(value=value)

    def SetValue(self, request: SetValueRequest, context: Any) -> SetValueResponse:  # noqa: N802
        """Trivial implementation for testing."""
        self._values[request.value_id] = request.value
        return SetValueResponse()

    def fail_next_open_panel(self) -> None:
        """Set whether the OpenPanel method should fail the next time it is called."""
        self._fail_next_open_panel = True
