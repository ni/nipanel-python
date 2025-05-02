"""Client for accessing the NI Python Panel Service."""

from __future__ import annotations

import logging
import threading
from typing import TypeVar, Callable

import grpc
from ni.pythonpanel.v1.python_panel_service_pb2 import OpenPanelRequest
from ni.pythonpanel.v1.python_panel_service_pb2_grpc import PythonPanelServiceStub
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool

from nipanel._typing import ParamSpec

_P = ParamSpec("_P")
_T = TypeVar("_T")

_logger = logging.getLogger(__name__)


class PanelClient:
    """Client for accessing the NI Python Panel Service."""

    def __init__(
        self,
        *,
        provided_interface: str,
        service_class: str,
        discovery_client: DiscoveryClient | None = None,
        grpc_channel_pool: GrpcChannelPool | None = None,
        grpc_channel: grpc.Channel | None = None,
    ) -> None:
        """Initialize the panel client.

        Args:
            provided_interface: The interface provided by the service.
            service_class: The class of the service.
            discovery_client: An optional discovery client.
            grpc_channel: An optional panel gRPC channel.
            grpc_channel_pool: An optional gRPC channel pool.
        """
        self._initialization_lock = threading.Lock()
        self._provided_interface = provided_interface
        self._service_class = service_class
        self._discovery_client = discovery_client
        self._grpc_channel_pool = grpc_channel_pool
        self._grpc_channel = grpc_channel
        self._stub: PythonPanelServiceStub | None = None

    def open_panel(self, panel_id: str, panel_uri: str) -> None:
        """Open the panel."""
        open_panel_request = OpenPanelRequest(panel_id=panel_id, panel_uri=panel_uri)
        self._invoke_with_retry(self._get_stub().OpenPanel, open_panel_request)

    def _get_stub(self) -> PythonPanelServiceStub:
        if self._stub is None:
            if self._grpc_channel is not None:
                self._stub = PythonPanelServiceStub(self._grpc_channel)
            else:
                with self._initialization_lock:
                    if self._grpc_channel_pool is None:
                        _logger.debug("Creating unshared GrpcChannelPool.")
                        self._grpc_channel_pool = GrpcChannelPool()
                    if self._discovery_client is None:
                        _logger.debug("Creating unshared DiscoveryClient.")
                        self._discovery_client = DiscoveryClient(
                            grpc_channel_pool=self._grpc_channel_pool
                        )

                    service_location = self._discovery_client.resolve_service(
                        provided_interface=self._provided_interface,
                        service_class=self._service_class,
                    )
                    channel = self._grpc_channel_pool.get_channel(service_location.insecure_address)
                    self._stub = PythonPanelServiceStub(channel)
        return self._stub

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
