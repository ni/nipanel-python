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

    def Connect(self, request: ConnectRequest, context: Any) -> ConnectResponse:  # noqa: N802
        """Just a trivial implementation for testing."""
        return ConnectResponse()

    def Disconnect(  # noqa: N802
        self, request: DisconnectRequest, context: Any
    ) -> DisconnectResponse:
        """Just a trivial implementation for testing."""
        return DisconnectResponse()

    def GetValue(self, request: GetValueRequest, context: Any) -> GetValueResponse:  # noqa: N802
        """Just a trivial implementation for testing."""
        value = self._values[request.value_id]
        return GetValueResponse(value=value)

    def SetValue(self, request: SetValueRequest, context: Any) -> SetValueResponse:  # noqa: N802
        """Just a trivial implementation for testing."""
        self._values[request.value_id] = request.value
        return SetValueResponse()
