"""Initializes a refresh component for Streamlit."""

from __future__ import annotations

import threading

from ni.measurementlink.discovery.v1.client import DiscoveryClient
from ni_grpc_extensions.channelpool import GrpcChannelPool
from streamlit.components.v1 import declare_component
from streamlit.components.v1.custom_component import CustomComponent


_grpc_client_lock = threading.RLock()
_panel_service_proxy_location: str | None = None


def initialize_refresh_component(panel_id: str) -> CustomComponent:
    """Initialize a refresh component to the Streamlit app."""
    proxy_base_address = _get_or_resolve_proxy()
    component_url = f"http://{proxy_base_address}/panel-service/refresh/{panel_id}"
    _refresh_component_func = declare_component(
        "panelRefreshComponent",
        url=component_url,
    )

    return _refresh_component_func


def _get_or_resolve_proxy() -> str:
    with _grpc_client_lock:
        global _panel_service_proxy_location
        if _panel_service_proxy_location is None:
            with GrpcChannelPool() as grpc_channel_pool:
                discovery_client = DiscoveryClient(grpc_channel_pool=grpc_channel_pool)
                service_location = discovery_client.resolve_service(
                    provided_interface="ni.http1.proxy",
                    service_class="",
                )
                _panel_service_proxy_location = service_location.insecure_address

        return _panel_service_proxy_location
