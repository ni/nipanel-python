"""Fixtures for testing."""

from collections.abc import Generator
from concurrent import futures

import grpc
import pytest
from ni.pythonpanel.v1.python_panel_service_pb2_grpc import (
    PythonPanelServiceStub,
)

from tests.utils._fake_python_panel_service import FakePythonPanelService


@pytest.fixture
def fake_python_panel_service() -> Generator[FakePythonPanelService]:
    """Fixture to create a FakePythonPanelServicer for testing."""
    with futures.ThreadPoolExecutor(max_workers=10) as thread_pool:
        service = FakePythonPanelService()
        service.start(thread_pool)
        yield service
        service.stop()


@pytest.fixture
def grpc_channel_to_fake_panel_service(
    fake_python_panel_service: FakePythonPanelService,
) -> Generator[grpc.Channel]:
    """Fixture to get a channel to the FakePythonPanelService."""
    service = fake_python_panel_service
    channel = grpc.insecure_channel(f"localhost:{service.port}")
    yield channel
    channel.close()


@pytest.fixture
def python_panel_service_stub(
    grpc_channel_to_fake_panel_service: grpc.Channel,
) -> Generator[PythonPanelServiceStub]:
    """Fixture to get a PythonPanelServiceStub, attached to a FakePythonPanelService."""
    channel = grpc_channel_to_fake_panel_service
    yield PythonPanelServiceStub(channel)
