from concurrent import futures

import grpc
from ni.panels.v1.panel_service_pb2_grpc import (
    add_PanelServiceServicer_to_server,
)

from tests.utils._fake_python_panel_servicer import FakePythonPanelServicer


class FakePythonPanelService:
    """Encapsulates a fake PythonPanelService with a gRPC server for testing."""

    def __init__(self) -> None:
        """Initialize the fake PythonPanelService."""
        self._server: grpc.Server
        self._port: int
        self._servicer = FakePythonPanelServicer()

    def start(self, thread_pool: futures.ThreadPoolExecutor) -> None:
        """Start the gRPC server and return the port it is bound to."""
        self._server = grpc.server(thread_pool)
        add_PanelServiceServicer_to_server(self._servicer, self._server)
        self._port = self._server.add_insecure_port("[::1]:0")
        self._server.start()

    def stop(self) -> None:
        """Stop the gRPC server."""
        if self._server:
            self._server.stop(None)

    @property
    def servicer(self) -> FakePythonPanelServicer:
        """Get the servicer instance."""
        return self._servicer

    @property
    def port(self) -> int:
        """Get the port the server is bound to."""
        return self._port
