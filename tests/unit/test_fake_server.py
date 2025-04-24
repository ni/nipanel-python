from concurrent import futures
from typing import Generator

import grpc
import pytest
from google.protobuf.any_pb2 import Any
from ni.pythonpanel.v1.python_panel_service_pb2 import (
    ConnectRequest,
    DisconnectRequest,
    GetValueRequest,
    SetValueRequest,
)
from ni.pythonpanel.v1.python_panel_service_pb2_grpc import PythonPanelServiceStub

from tests.utils._fake_python_panel_service import FakePythonPanelService


@pytest.fixture
def grpc_server() -> Generator[tuple[grpc.Server, int], Any, None]:
    # Create an in-process gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = FakePythonPanelService()
    from ni.pythonpanel.v1.python_panel_service_pb2_grpc import (
        add_PythonPanelServiceServicer_to_server,
    )

    add_PythonPanelServiceServicer_to_server(servicer, server)
    port = server.add_insecure_port("[::]:0")  # Bind to an available port
    server.start()
    yield server, port
    server.stop(None)


@pytest.fixture
def grpc_client(
    grpc_server: tuple[grpc.Server, int],
) -> Generator[PythonPanelServiceStub, Any, None]:
    _, port = grpc_server
    channel = grpc.insecure_channel(f"localhost:{port}")
    yield PythonPanelServiceStub(channel)
    channel.close()


def test___connect___gets_response(grpc_client: PythonPanelServiceStub) -> None:
    request = ConnectRequest(panel_id="test_panel", panel_uri="path/to/panel")
    response = grpc_client.Connect(request)
    assert response is not None  # Ensure response is returned


def test___disconnect___gets_response(grpc_client: PythonPanelServiceStub) -> None:
    request = DisconnectRequest(panel_id="test_panel")
    response = grpc_client.Disconnect(request)
    assert response is not None  # Ensure response is returned


def test___get_value___gets_response(grpc_client: PythonPanelServiceStub) -> None:
    request = GetValueRequest(panel_id="test_panel", value_id="test_value")
    response = grpc_client.GetValue(request)
    assert response is not None  # Ensure response is returned
    assert isinstance(response.value, Any)  # Ensure the value is of type `Any`


def test___set_value___gets_response(grpc_client: PythonPanelServiceStub) -> None:
    value = Any()
    value.value = b"test_data"
    request = SetValueRequest(panel_id="test_panel", value_id="test_value", value=value)
    response = grpc_client.SetValue(request)
    assert response is not None  # Ensure response is returned
