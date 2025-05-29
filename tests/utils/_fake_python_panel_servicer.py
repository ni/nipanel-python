from typing import Any

import grpc
from ni.pythonpanel.v1.python_panel_service_pb2 import (
    OpenPanelRequest,
    OpenPanelResponse,
    ClosePanelRequest,
    ClosePanelResponse,
    EnumeratePanelsRequest,
    EnumeratePanelsResponse,
    PanelInformation,
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
        self._panel_ids: list[str] = []
        self._panel_is_open: dict[str, bool] = {}
        self._panel_value_ids: dict[str, dict[str, Any]] = {}
        self._fail_next_open_panel = False

    def OpenPanel(self, request: OpenPanelRequest, context: Any) -> OpenPanelResponse:  # noqa: N802
        """Trivial implementation for testing."""
        if self._fail_next_open_panel:
            self._fail_next_open_panel = False
            context.abort(grpc.StatusCode.UNAVAILABLE, "Simulated failure")
        self._open_panel(request.panel_id)
        return OpenPanelResponse()

    def ClosePanel(  # noqa: N802
        self, request: ClosePanelRequest, context: Any
    ) -> ClosePanelResponse:
        """Trivial implementation for testing."""
        self._close_panel(request.reset, request.panel_id)
        return ClosePanelResponse()

    def EnumeratePanels(  # noqa: N802
        self, request: EnumeratePanelsRequest, context: Any
    ) -> EnumeratePanelsResponse:
        """Trivial implementation for testing."""
        response = EnumeratePanelsResponse()
        for panel_id in self._panel_ids:
            panel = PanelInformation(
                panel_id=panel_id,
                is_open=self._panel_is_open[panel_id],
                value_ids=self._panel_value_ids[panel_id],
            )
            response.panels.append(panel)
        return response

    def GetValue(self, request: GetValueRequest, context: Any) -> GetValueResponse:  # noqa: N802
        """Trivial implementation for testing."""
        value = self._panel_value_ids[request.panel_id][request.value_id]
        return GetValueResponse(value=value)

    def SetValue(self, request: SetValueRequest, context: Any) -> SetValueResponse:  # noqa: N802
        """Trivial implementation for testing."""
        self._init_panel(request.panel_id)
        self._panel_value_ids[request.panel_id][request.value_id] = request.value
        return SetValueResponse()

    def fail_next_open_panel(self) -> None:
        """Set whether the OpenPanel method should fail the next time it is called."""
        self._fail_next_open_panel = True

    def _init_panel(self, panel_id: str) -> None:
        if panel_id not in self._panel_ids:
            self._panel_ids.append(panel_id)
            self._panel_is_open[panel_id] = False
            self._panel_value_ids[panel_id] = {}

    def _open_panel(self, panel_id: str) -> None:
        if panel_id not in self._panel_ids:
            self._panel_ids.append(panel_id)
            self._panel_is_open[panel_id] = True
            self._panel_value_ids[panel_id] = {}
        else:
            self._panel_is_open[panel_id] = True

    def _close_panel(self, reset: bool, panel_id: str) -> None:
        if reset:
            self._panel_ids.remove(panel_id)
            self._panel_is_open.pop(panel_id)
            self._panel_value_ids.pop(panel_id)
        else:
            self._panel_is_open[panel_id] = False
