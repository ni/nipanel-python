from __future__ import annotations

import logging
import threading
from typing import Callable, TypeVar

import grpc
from ni.pythonpanel.v1.python_panel_service_pb2 import (
    StartPanelRequest,
    StopPanelRequest,
    EnumeratePanelsRequest,
    GetValueRequest,
    TryGetValueRequest,
    SetValueRequest,
)
from ni.pythonpanel.v1.python_panel_service_pb2_grpc import PythonPanelServiceStub
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool
from typing_extensions import ParamSpec

from nipanel._convert import (
    from_any,
    to_any,
)

_P = ParamSpec("_P")
_T = TypeVar("_T")

_logger = logging.getLogger(__name__)


class _PanelClient:
    def __init__(
        self,
        *,
        provided_interface: str,
        service_class: str,
        discovery_client: DiscoveryClient | None = None,
        grpc_channel_pool: GrpcChannelPool | None = None,
        grpc_channel: grpc.Channel | None = None,
    ) -> None:
        self._initialization_lock = threading.Lock()
        self._provided_interface = provided_interface
        self._service_class = service_class
        self._discovery_client = discovery_client
        self._grpc_channel_pool = grpc_channel_pool
        self._grpc_channel = grpc_channel
        self._stub: PythonPanelServiceStub | None = None

    def start_panel(self, panel_id: str, panel_script_path: str, python_path: str) -> str:
        start_panel_request = StartPanelRequest(
            panel_id=panel_id, panel_script_path=panel_script_path, python_path=python_path
        )
        response = self._invoke_with_retry(self._get_stub().StartPanel, start_panel_request)
        return response.panel_url

    def stop_panel(self, panel_id: str, reset: bool) -> None:
        stop_panel_request = StopPanelRequest(panel_id=panel_id, reset=reset)
        self._invoke_with_retry(self._get_stub().StopPanel, stop_panel_request)

    def enumerate_panels(self) -> dict[str, tuple[str, list[str]]]:
        enumerate_panels_request = EnumeratePanelsRequest()
        response = self._invoke_with_retry(
            self._get_stub().EnumeratePanels, enumerate_panels_request
        )
        return {
            panel.panel_id: (panel.panel_url, list(panel.value_ids)) for panel in response.panels
        }

    def set_value(self, panel_id: str, value_id: str, value: object, notify: bool) -> None:
        new_any = to_any(value)
        set_value_request = SetValueRequest(
            panel_id=panel_id, value_id=value_id, value=new_any, notify=notify
        )
        self._invoke_with_retry(self._get_stub().SetValue, set_value_request)

    def get_value(self, panel_id: str, value_id: str) -> object:
        get_value_request = GetValueRequest(panel_id=panel_id, value_id=value_id)
        response = self._invoke_with_retry(self._get_stub().GetValue, get_value_request)
        return from_any(response.value)

    def try_get_value(self, panel_id: str, value_id: str) -> object | None:
        try_get_value_request = TryGetValueRequest(panel_id=panel_id, value_id=value_id)
        response = self._invoke_with_retry(self._get_stub().TryGetValue, try_get_value_request)
        if response.HasField("value"):
            return from_any(response.value)
        else:
            return None

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
