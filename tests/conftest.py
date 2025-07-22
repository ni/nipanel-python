"""Fixtures for testing."""

from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor
from typing import cast

import grpc
import pytest
from grpc.framework.foundation import logging_pool
from ni.panels.v1.panel_service_pb2_grpc import PanelServiceStub

from tests.utils._fake_python_panel_service import FakePythonPanelService


@pytest.fixture
def fake_python_panel_service() -> Generator[FakePythonPanelService]:
    """Fixture to create a FakePythonPanelServicer for testing."""
    with logging_pool.pool(max_workers=10) as thread_pool:
        # _LoggingPool is not a ThreadPoolExecutor, but it's duck-typing compatible with one.
        thread_pool = cast(ThreadPoolExecutor, thread_pool)
        service = FakePythonPanelService()
        service.start(thread_pool)
        yield service
        service.stop()


@pytest.fixture
def fake_panel_channel(
    fake_python_panel_service: FakePythonPanelService,
) -> Generator[grpc.Channel]:
    """Fixture to get a channel to the FakePythonPanelService."""
    service = fake_python_panel_service
    channel = grpc.insecure_channel(f"localhost:{service.port}")
    yield channel
    channel.close()


@pytest.fixture
def python_panel_service_stub(
    fake_panel_channel: grpc.Channel,
) -> Generator[PanelServiceStub]:
    """Fixture to get a PanelServiceStub, attached to a FakePythonPanelService."""
    yield PanelServiceStub(fake_panel_channel)
