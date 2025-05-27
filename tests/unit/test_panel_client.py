import grpc
import pytest

from nipanel._panel_client import PanelClient


def test___enumerate_is_empty(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    assert client.enumerate_panels() == []


def test___open_panels___enumerate_has_panels(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    client.open_panel("panel1", "uri1")
    client.open_panel("panel2", "uri2")

    assert client.enumerate_panels() == ["panel1", "panel2"]


def test___open_panels___close_panel_1___enumerate_has_panel_2(
    fake_panel_channel: grpc.Channel,
) -> None:
    client = create_panel_client(fake_panel_channel)
    client.open_panel("panel1", "uri1")
    client.open_panel("panel2", "uri2")

    client.close_panel("panel1", reset=False)

    assert client.enumerate_panels() == ["panel2"]


def test___get_unset_value_raises_exception(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    with pytest.raises(Exception):
        client.get_value("panel1", "unset_id")


def test___set_value___gets_value(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    client.set_value("panel1", "val1", "value1")

    assert client.get_value("panel1", "val1") == "value1"


def create_panel_client(fake_panel_channel: grpc.Channel) -> PanelClient:
    return PanelClient(
        provided_interface="iface",
        service_class="svc",
        grpc_channel=fake_panel_channel,
    )
