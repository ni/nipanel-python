from __future__ import annotations

import sys
from abc import ABC
from pathlib import Path

import grpc
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool

from nipanel._panel_value_accessor import PanelValueAccessor


class Panel(PanelValueAccessor, ABC):
    """This class allows you to open a panel and specify values for its controls."""

    __slots__ = ["_panel_script_path", "_panel_url"]

    def __init__(
        self,
        *,
        panel_id: str,
        panel_script_path: str,
        provided_interface: str,
        service_class: str,
        discovery_client: DiscoveryClient | None = None,
        grpc_channel_pool: GrpcChannelPool | None = None,
        grpc_channel: grpc.Channel | None = None,
    ) -> None:
        """Initialize the panel."""
        super().__init__(
            panel_id=panel_id,
            provided_interface=provided_interface,
            service_class=service_class,
            discovery_client=discovery_client,
            grpc_channel_pool=grpc_channel_pool,
            grpc_channel=grpc_channel,
        )
        self._panel_script_path = panel_script_path
        python_path = self._get_python_path()
        self._panel_url = self._panel_client.start_panel(panel_id, panel_script_path, python_path)

    @property
    def panel_script_path(self) -> str:
        """Read-only accessor for the panel script path."""
        return self._panel_script_path

    @property
    def panel_url(self) -> str:
        """Read-only accessor for the panel URL."""
        return self._panel_url

    def _get_python_path(self) -> str:
        """Get the Python interpreter path for the panel that ensures the same environment."""
        if sys.executable is None or sys.executable == "":
            raise RuntimeError("Python environment not found")
        if getattr(sys, "frozen", False):
            raise RuntimeError("Panel cannot be used in a frozen application (e.g., PyInstaller).")

        if sys.prefix != sys.base_prefix:
            # If we're in a virtual environment, build the path to the Python executable
            # On Linux: .venv/bin/python, On Windows: .venv\Scripts\python.exe
            if sys.platform.startswith("win"):
                python_executable = "python.exe"
                bin_dir = "Scripts"
            else:
                python_executable = "python"
                bin_dir = "bin"

            # Construct path to the Python in the virtual environment based on sys.prefix
            python_path = str(Path(sys.prefix) / bin_dir / python_executable)

            # Fall back to sys.executable if the constructed path doesn't exist
            if not Path(python_path).exists():
                python_path = str(Path(sys.executable).resolve())
        else:
            # If not in a .venv environment, use sys.executable
            python_path = str(Path(sys.executable).resolve())

        if sys.prefix not in python_path:
            # Ensure the Python path is within the current environment
            raise RuntimeError(
                f"Python path '{python_path}' does not match the current environment prefix '{sys.prefix}'."
            )

        return python_path
