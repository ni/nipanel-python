"""Fixtures for testing gRPC services."""

from concurrent import futures
from typing import Any, Generator

import grpc
import pytest
from ni.pythonpanel.v1.python_panel_service_pb2_grpc import (
    PythonPanelServiceStub,
    add_PythonPanelServiceServicer_to_server,
)

from tests.utils._fake_python_panel_servicer import FakePythonPanelServicer


@pytest.fixture
def fake_python_panel_service() -> Generator[tuple[grpc.Server, int], Any, None]:
    """Fixture to create a FakePythonPanelServicer for testing."""
    # Create an in-process gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = FakePythonPanelServicer()

    add_PythonPanelServiceServicer_to_server(servicer, server)
    port = server.add_insecure_port("[::]:0")  # Bind to an available port
    server.start()
    yield server, port
    server.stop(None)


@pytest.fixture
def fake_python_panel_service_stub(
    fake_python_panel_service: tuple[grpc.Server, int],
) -> Generator[PythonPanelServiceStub, Any, None]:
    """Fixture to create a gRPC stub for the FakePythonPanelService."""
    _, port = fake_python_panel_service
    channel = grpc.insecure_channel(f"localhost:{port}")
    yield PythonPanelServiceStub(channel)
    channel.close()
