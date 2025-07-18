"""Initializes a refresh component for Streamlit."""

from __future__ import annotations

from typing import ClassVar

from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool
from streamlit.components.v1 import declare_component
from streamlit.components.v1.custom_component import CustomComponent


class _ServiceResolver:

    _panel_service_proxy_location: ClassVar[str | None] = None

    @classmethod
    def get_or_resolve_proxy(cls) -> str:
        if cls._panel_service_proxy_location is None:
            discovery_client = DiscoveryClient(grpc_channel_pool=GrpcChannelPool())
            service_location = discovery_client.resolve_service(
                provided_interface="ni.http1.proxy",
                service_class="",
            )
            cls._panel_service_proxy_location = service_location.insecure_address

        return cls._panel_service_proxy_location


def initialize_refresh_component(panel_id: str) -> CustomComponent:
    """Initialize a refresh component to the Streamlit app."""
    proxy_base_address = _ServiceResolver.get_or_resolve_proxy()
    component_url = f"http://{proxy_base_address}/panel-service/refresh/{panel_id}"
    _refresh_component_func = declare_component(
        "panelRefreshComponent",
        url=component_url,
    )

    return _refresh_component_func
