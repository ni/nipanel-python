from typing import Any

import google.protobuf.any_pb2 as any_pb2
import grpc
from ni.pythonpanel.v1.python_panel_service_pb2 import (
    OpenPanelRequest,
    OpenPanelResponse,
    GetValueRequest,
    GetValueResponse,
    SetValueRequest,
    SetValueResponse,
)
from ni.pythonpanel.v1.python_panel_service_pb2_grpc import PythonPanelServiceServicer


class FakePythonPanelServicer(PythonPanelServiceServicer):
    """Fake implementation of the PythonPanelServicer for testing."""

    _values = {"test_value": any_pb2.Any()}
    _fail_next_open_panel = False

    def OpenPanel(self, request: OpenPanelRequest, context: Any) -> OpenPanelResponse:  # noqa: N802
        """Trivial implementation for testing."""
        if self._fail_next_open_panel:
            self._fail_next_open_panel = False
            context.abort(grpc.StatusCode.UNAVAILABLE, "Simulated failure")
        return OpenPanelResponse()

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
