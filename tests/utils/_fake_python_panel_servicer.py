from typing import Any

import google.protobuf.any_pb2 as any_pb2
from ni.pythonpanel.v1.python_panel_service_pb2 import (
    ConnectRequest,
    ConnectResponse,
    DisconnectRequest,
    DisconnectResponse,
    GetValueRequest,
    GetValueResponse,
    SetValueRequest,
    SetValueResponse,
)
from ni.pythonpanel.v1.python_panel_service_pb2_grpc import PythonPanelServiceServicer


class FakePythonPanelServicer(PythonPanelServiceServicer):
    """Fake implementation of the PythonPanelServicer for testing."""

    _values = {"test_value": any_pb2.Any()}
    _fail_next_connect = False

    def Connect(self, request: ConnectRequest, context: Any) -> ConnectResponse:  # noqa: N802
        """Trivial implementation for testing."""
        if self._fail_next_connect:
            self._fail_next_connect = False
            raise ValueError("Simulate a failure to Connect.")
        return ConnectResponse()

    def Disconnect(  # noqa: N802
        self, request: DisconnectRequest, context: Any
    ) -> DisconnectResponse:
        """Trivial implementation for testing."""
        return DisconnectResponse()

    def GetValue(self, request: GetValueRequest, context: Any) -> GetValueResponse:  # noqa: N802
        """Trivial implementation for testing."""
        value = self._values[request.value_id]
        return GetValueResponse(value=value)

    def SetValue(self, request: SetValueRequest, context: Any) -> SetValueResponse:  # noqa: N802
        """Trivial implementation for testing."""
        self._values[request.value_id] = request.value
        return SetValueResponse()

    def fail_next_connect(self) -> None:
        """Set whether the Connect method should fail the next time it is called."""
        self._fail_next_connect = True
