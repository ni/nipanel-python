from __future__ import annotations

import collections
import enum
from abc import ABC
from typing import TypeVar, overload

import grpc
import hightime as ht
import nitypes.bintime as bt
from ni.measurementlink.discovery.v1.client import DiscoveryClient
from ni_grpc_extensions.channelpool import GrpcChannelPool
from nitypes.time import convert_datetime, convert_timedelta

from nipanel._panel_client import _PanelClient

_T = TypeVar("_T")


class PanelValueAccessor(ABC):
    """This class allows you to access values for a panel's controls."""

    __slots__ = [
        "_panel_client",
        "_panel_id",
        "_notify_on_set_value",
        "_last_values",
        "__weakref__",
    ]

    def __init__(
        self,
        *,
        panel_id: str,
        notify_on_set_value: bool = True,
        discovery_client: DiscoveryClient | None = None,
        grpc_channel_pool: GrpcChannelPool | None = None,
        grpc_channel: grpc.Channel | None = None,
    ) -> None:
        """Initialize the accessor."""
        self._panel_client = _PanelClient(
            discovery_client=discovery_client,
            grpc_channel_pool=grpc_channel_pool,
            grpc_channel=grpc_channel,
        )
        self._panel_id = panel_id
        self._notify_on_set_value = notify_on_set_value
        self._last_values: collections.defaultdict[str, object] = collections.defaultdict(
            lambda: object()
        )

    @property
    def panel_id(self) -> str:
        """Read-only accessor for the panel ID."""
        return self._panel_id

    @overload
    def get_value(self, value_id: str) -> object: ...

    @overload
    def get_value(self, value_id: str, default_value: _T) -> _T: ...

    def get_value(self, value_id: str, default_value: _T | None = None) -> _T | object:
        """Get the value for a control on the panel with an optional default value.

        Args:
            value_id: The id of the value
            default_value: The default value to return if the value is not set

        Returns:
            The value, or the default value if not set. The returned value will
            have the same type as default_value, if one was provided.

        Raises:
            KeyError: If the value is not set and no default value is provided
        """
        value = self._panel_client.try_get_value(self._panel_id, value_id)
        if value is None:
            if default_value is not None:
                return default_value
            raise KeyError(f"Value with id '{value_id}' not found on panel '{self._panel_id}'.")

        if default_value is not None and not isinstance(value, type(default_value)):
            if isinstance(default_value, enum.Enum):
                enum_type = type(default_value)
                return enum_type(value)

            # The grpc converter always converts PrecisionTimestamp into ht.datetime, so
            # we need to handle the case where they provide a bt.DateTime default by
            # converting to bintime.
            if isinstance(default_value, bt.DateTime) and isinstance(value, ht.datetime):
                return convert_datetime(bt.DateTime, value)

            # The grpc converter always converts PrecisionDuration into ht.timedelta, so
            # we need to handle the case where they provide a bt.TimeDelta default by
            # converting to bintime.
            if isinstance(default_value, bt.TimeDelta) and isinstance(value, ht.timedelta):
                return convert_timedelta(bt.TimeDelta, value)

            # lists are allowed to not match, since sets and tuples are converted to lists
            if not isinstance(value, list):
                raise TypeError(
                    f"Value type {type(value).__name__} does not match default value type {type(default_value).__name__}."
                )

        return value

    def set_value(self, value_id: str, value: object) -> None:
        """Set the value for a control on the panel.

        Args:
            value_id: The id of the value
            value: The value
        """
        if isinstance(value, enum.Enum):
            value = value.value

        self._panel_client.set_value(
            self._panel_id, value_id, value, notify=self._notify_on_set_value
        )
        self._last_values[value_id] = value

    def set_value_if_changed(self, value_id: str, value: object) -> None:
        """Set the value for a control on the panel only if it has changed since the last call.

        This method helps reduce unnecessary updates when the value hasn't changed.

        Args:
            value_id: The id of the value
            value: The value to set
        """
        if value != self._last_values[value_id]:
            self.set_value(value_id, value)
