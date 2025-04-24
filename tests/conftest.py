"""Fixtures for testing."""

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
def fake_python_panel_service() -> Generator[tuple[FakePythonPanelServicer, int], Any, None]:
    """Fixture to create a FakePythonPanelServicer for testing."""
    thread_pool = futures.ThreadPoolExecutor(max_workers=10)
    server = grpc.server(thread_pool)
    servicer = FakePythonPanelServicer()
    add_PythonPanelServiceServicer_to_server(servicer, server)
    port = server.add_insecure_port("[::]:0")
    server.start()
    yield servicer, port
    server.stop(None)


@pytest.fixture
def fake_python_panel_service_stub(
    fake_python_panel_service: tuple[FakePythonPanelServicer, int],
) -> Generator[PythonPanelServiceStub, Any, None]:
    """Fixture to attach a PythonPanelSericeStub to a FakePythonPanelService."""
    _, port = fake_python_panel_service
    channel = grpc.insecure_channel(f"localhost:{port}")
    yield PythonPanelServiceStub(channel)
    channel.close()
