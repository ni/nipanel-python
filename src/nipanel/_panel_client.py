"""Client for accessing the NI Python Panel Service."""

from __future__ import annotations

import logging
import threading
from typing import Callable

import grpc
from ni.pythonpanel.v1.python_panel_service_pb2 import ConnectRequest, DisconnectRequest
from ni.pythonpanel.v1.python_panel_service_pb2_grpc import PythonPanelServiceStub
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool
from typing_extensions import ParamSpec, TypeVar

_logger = logging.getLogger(__name__)


class PanelClient:
    """Client for accessing the NI Python Panel Service."""

    def __init__(
        self,
        resolve_service_address_fn: Callable[[DiscoveryClient], str],
        *,
        discovery_client: DiscoveryClient | None = None,
        grpc_channel: grpc.Channel | None = None,
        grpc_channel_pool: GrpcChannelPool | None = None,
    ) -> None:
        """Initialize the panel client.

        Args:
            resolve_service_address_fn: A function to resolve the service location.
            discovery_client: An optional discovery client.
            grpc_channel: An optional panel gRPC channel.
            grpc_channel_pool: An optional gRPC channel pool.
        """
        self._initialization_lock = threading.Lock()
        self._resolve_service_address_fn = resolve_service_address_fn
        self._discovery_client = discovery_client
        self._grpc_channel_pool = grpc_channel_pool
        self._stub: PythonPanelServiceStub | None = None

        if grpc_channel is not None:
            self._stub = PythonPanelServiceStub(grpc_channel)

    def connect(self, panel_id: str, panel_uri: str) -> None:
        """Connect to the panel and open it."""
        connect_request = ConnectRequest(panel_id=panel_id, panel_uri=panel_uri)
        self._invoke_with_retry(self._get_stub().Connect, connect_request)

    def disconnect(self, panel_id: str) -> None:
        """Disconnect from the panel (does not close the panel)."""
        disconnect_request = DisconnectRequest(panel_id=panel_id)
        self._invoke_with_retry(self._get_stub().Disconnect, disconnect_request)

    def _get_stub(self) -> PythonPanelServiceStub:
        if self._stub is None:
            with self._initialization_lock:
                if self._grpc_channel_pool is None:
                    _logger.debug("Creating unshared GrpcChannelPool.")
                    self._grpc_channel_pool = GrpcChannelPool()
                if self._discovery_client is None:
                    _logger.debug("Creating unshared DiscoveryClient.")
                    self._discovery_client = DiscoveryClient(
                        grpc_channel_pool=self._grpc_channel_pool
                    )
                if self._stub is None:
                    service_address = self._resolve_service_address_fn(self._discovery_client)
                    channel = self._grpc_channel_pool.get_channel(service_address)
                    self._stub = PythonPanelServiceStub(channel)
        return self._stub

    _T = TypeVar("_T")
    _P = ParamSpec("_P")

    def _invoke_with_retry(
        self, method: Callable[_P, _T], *args: _P.args, **kwargs: _P.kwargs
    ) -> _T:
        """Invoke a gRPC method with retry logic."""
        try:
            return method(*args, **kwargs)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE or e.code() == grpc.StatusCode.UNKNOWN:
                # if the service is unavailable, we can retry the connection
                self._stub = None
                return method(*args, **kwargs)
            raise
