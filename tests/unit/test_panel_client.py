import grpc
import pytest

from nipanel._panel_client import PanelClient


def test___enumerate_is_empty(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    assert client.enumerate_panels() == {}


def test___start_panels___enumerate_has_panels(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    client.start_panel("panel1", "uri1")
    client.start_panel("panel2", "uri2")

    assert client.enumerate_panels() == {
        "panel1": ("http://localhost:50051/panel1", []),
        "panel2": ("http://localhost:50051/panel2", []),
    }


def test___start_panels___stop_panel_1_with_reset___enumerate_has_panel_2(
    fake_panel_channel: grpc.Channel,
) -> None:
    client = create_panel_client(fake_panel_channel)
    client.start_panel("panel1", "uri1")
    client.start_panel("panel2", "uri2")

    client.stop_panel("panel1", reset=True)

    assert client.enumerate_panels() == {
        "panel2": ("http://localhost:50051/panel2", []),
    }


def test___start_panels___stop_panel_1_without_reset___enumerate_has_both_panels(
    fake_panel_channel: grpc.Channel,
) -> None:
    client = create_panel_client(fake_panel_channel)
    client.start_panel("panel1", "uri1")
    client.start_panel("panel2", "uri2")

    client.stop_panel("panel1", reset=False)

    assert client.enumerate_panels() == {
        "panel1": ("", []),
        "panel2": ("http://localhost:50051/panel2", []),
    }


def test___get_unset_value_raises_exception(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    with pytest.raises(Exception):
        client.get_value("panel1", "unset_id")


def test___set_value___enumerate_panels_shows_value(
    fake_panel_channel: grpc.Channel,
) -> None:
    client = create_panel_client(fake_panel_channel)

    client.set_value("panel1", "val1", "value1", notify=False)

    assert client.enumerate_panels() == {"panel1": ("", ["val1"])}


def test___set_value___gets_value(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    client.set_value("panel1", "val1", "value1", notify=False)

    assert client.get_value("panel1", "val1") == "value1"


def test___set_values___enumerate_panels_shows_values(
    fake_panel_channel: grpc.Channel,
) -> None:
    client = create_panel_client(fake_panel_channel)

    values = {"val1": "value1", "val2": 42, "val3": True}

    client.set_values("panel1", values, notify=False)

    assert client.enumerate_panels() == {"panel1": ("", ["val1", "val2", "val3"])}


def test___set_values___gets_values(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    values = {"val1": "value1", "val2": 42, "val3": True}

    client.set_values("panel1", values, notify=False)

    assert client.get_value("panel1", "val1") == "value1"
    assert client.get_value("panel1", "val2") == 42
    assert client.get_value("panel1", "val3") is True


def test___set_values_empty_dict___has_no_effect(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    client.set_values("panel1", {}, notify=False)

    assert client.enumerate_panels() == {"panel1": ("", [])}


def test___set_values_then_set_value___both_values_accessible(
    fake_panel_channel: grpc.Channel,
) -> None:
    client = create_panel_client(fake_panel_channel)

    client.set_values("panel1", {"val1": "batch value", "val2": 42}, notify=False)
    client.set_value("panel1", "val3", "individual value", notify=False)

    assert client.get_value("panel1", "val1") == "batch value"
    assert client.get_value("panel1", "val2") == 42
    assert client.get_value("panel1", "val3") == "individual value"
    assert client.enumerate_panels() == {"panel1": ("", ["val1", "val2", "val3"])}


def create_panel_client(fake_panel_channel: grpc.Channel) -> PanelClient:
    return PanelClient(
        provided_interface="iface",
        service_class="svc",
        grpc_channel=fake_panel_channel,
    )
