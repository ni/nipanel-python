import grpc
import pytest

from nipanel._panel_client import PanelClient


def test___enumerate_panels_is_empty(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    assert client.enumerate_panels() == {}


def test___open_panels___both_panels_open_and_in_memory(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    client.open_panel("panel1", "uri1")
    client.open_panel("panel2", "uri2")

    assert client.enumerate_panels() == {
        "panel1": (True, []),
        "panel2": (True, []),
    }


def test___open_panels___close_panel_1_with_reset___panel_1_not_in_memory(
    fake_panel_channel: grpc.Channel,
) -> None:
    client = create_panel_client(fake_panel_channel)
    client.open_panel("panel1", "uri1")
    client.open_panel("panel2", "uri2")

    client.close_panel("panel1", reset=True)

    assert client.enumerate_panels() == {
        "panel2": (True, []),
    }


def test___open_panels___close_panel_1_without_reset___both_panels_in_memory(
    fake_panel_channel: grpc.Channel,
) -> None:
    client = create_panel_client(fake_panel_channel)
    client.open_panel("panel1", "uri1")
    client.open_panel("panel2", "uri2")

    client.close_panel("panel1", reset=False)

    assert client.enumerate_panels() == {
        "panel1": (False, []),
        "panel2": (True, []),
    }


def test___get_unset_value_raises_exception(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    with pytest.raises(Exception):
        client.get_value("panel1", "unset_id")


def test___set_value___enumerate_panels_shows_value(
    fake_panel_channel: grpc.Channel,
) -> None:
    client = create_panel_client(fake_panel_channel)

    client.set_value("panel1", "val1", "value1")

    assert client.enumerate_panels() == {"panel1": (False, ["val1"])}


def test___set_value___clear_value___enumerate_panels_shows_no_value(
    fake_panel_channel: grpc.Channel,
) -> None:
    client = create_panel_client(fake_panel_channel)
    client.set_value("panel1", "val1", "value1")

    client.clear_value("panel1", "val1")

    assert client.enumerate_panels() == {"panel1": (False, [])}


def test___set_values___clear_value_2___enumerate_panels_has_value_1(
    fake_panel_channel: grpc.Channel,
) -> None:
    client = create_panel_client(fake_panel_channel)
    client.set_value("panel1", "val1", "value1")
    client.set_value("panel1", "val2", "value2")

    client.clear_value("panel1", "val2")

    assert client.enumerate_panels() == {"panel1": (False, ["val1"])}


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
