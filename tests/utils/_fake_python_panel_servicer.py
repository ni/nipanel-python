from typing import Any

import grpc
from ni.pythonpanel.v1.python_panel_service_pb2 import (
    StartPanelRequest,
    StartPanelResponse,
    StopPanelRequest,
    StopPanelResponse,
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
        self._panel_is_running: dict[str, bool] = {}
        self._panel_value_ids: dict[str, dict[str, Any]] = {}
        self._fail_next_start_panel = False
        self._notification_count: int = 0

    def StartPanel(  # noqa: N802
        self, request: StartPanelRequest, context: Any
    ) -> StartPanelResponse:
        """Trivial implementation for testing."""
        if self._fail_next_start_panel:
            self._fail_next_start_panel = False
            context.abort(grpc.StatusCode.UNAVAILABLE, "Simulated failure")
        self._start_panel(request.panel_id)
        return StartPanelResponse(panel_url=self._get_panel_url(request.panel_id))

    def StopPanel(self, request: StopPanelRequest, context: Any) -> StopPanelResponse:  # noqa: N802
        """Trivial implementation for testing."""
        self._stop_panel(request.reset, request.panel_id)
        return StopPanelResponse()

    def EnumeratePanels(  # noqa: N802
        self, request: EnumeratePanelsRequest, context: Any
    ) -> EnumeratePanelsResponse:
        """Trivial implementation for testing."""
        response = EnumeratePanelsResponse()
        for panel_id in self._panel_ids:
            panel = PanelInformation(
                panel_id=panel_id,
                panel_url=self._get_panel_url(panel_id),
                value_ids=self._panel_value_ids[panel_id],
            )
            response.panels.append(panel)
        return response

    def GetValue(self, request: GetValueRequest, context: Any) -> GetValueResponse:  # noqa: N802
        """Trivial implementation for testing."""
        if request.value_id not in self._panel_value_ids.get(request.panel_id, {}):
            context.abort(grpc.StatusCode.NOT_FOUND, "Value ID not found in panel")
        value = self._panel_value_ids[request.panel_id][request.value_id]
        return GetValueResponse(value=value)

    def SetValue(self, request: SetValueRequest, context: Any) -> SetValueResponse:  # noqa: N802
        """Trivial implementation for testing."""
        self._init_panel(request.panel_id)
        self._panel_value_ids[request.panel_id][request.value_id] = request.value
        if request.notify:
            self._notification_count += 1
        return SetValueResponse()

    def fail_next_start_panel(self) -> None:
        """Set whether the StartPanel method should fail the next time it is called."""
        self._fail_next_start_panel = True

    @property
    def notification_count(self) -> int:
        """Get the number of notifications sent from SetValue."""
        return self._notification_count

    def _init_panel(self, panel_id: str) -> None:
        if panel_id not in self._panel_ids:
            self._panel_ids.append(panel_id)
            self._panel_is_running[panel_id] = False
            self._panel_value_ids[panel_id] = {}

    def _start_panel(self, panel_id: str) -> None:
        if panel_id not in self._panel_ids:
            self._panel_ids.append(panel_id)
            self._panel_is_running[panel_id] = True
            self._panel_value_ids[panel_id] = {}
        else:
            self._panel_is_running[panel_id] = True

    def _stop_panel(self, reset: bool, panel_id: str) -> None:
        if reset:
            self._panel_ids.remove(panel_id)
            self._panel_is_running.pop(panel_id)
            self._panel_value_ids.pop(panel_id)
        else:
            self._panel_is_running[panel_id] = False

    def _get_panel_url(self, panel_id: str) -> str:
        if not self._panel_is_running.get(panel_id, False):
            return ""
        return f"http://localhost:50051/{panel_id}"
