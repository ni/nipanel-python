from concurrent import futures
from typing import Generator

import grpc
import pytest
from google.protobuf.any_pb2 import Any

from tests.utils._fake_panel import FakePanel
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


def test___panel___has_panel_id_and_panel_uri() -> None:
    panel = FakePanel(0, "my_panel", "path/to/script")
    assert panel.panel_id == "my_panel"
    assert panel.panel_uri == "path/to/script"


def test___connected_panel___set_value___gets_same_value(
    grpc_server: tuple[grpc.Server, int],
) -> None:
    _, port = grpc_server
    panel = FakePanel(port, "my_panel", "path/to/script")
    panel.connect()

    panel.set_value("test_id", "test_value")

    # TODO: AB#3095681 - change asserted value to test_value
    assert panel.get_value("test_id") == "placeholder value"
    panel.disconnect()


def test___with_panel___set_value___gets_same_value(grpc_server: tuple[grpc.Server, int]) -> None:
    _, port = grpc_server
    with FakePanel(port, "my_panel", "path/to/script") as panel:
        panel.set_value("test_id", "test_value")

        # TODO: AB#3095681 - change asserted value to test_value
        assert panel.get_value("test_id") == "placeholder value"
