import grpc

from nipanel._panel_client import PanelClient


def test___enumerate_is_empty(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    assert client.enumerate_panels() == {}


def test___start_panels___enumerate_has_panels(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    client.start_panel("panel1", "uri1", "python.exe")
    client.start_panel("panel2", "uri2", "python.exe")

    assert client.enumerate_panels() == {
        "panel1": ("http://localhost:50051/panel1", []),
        "panel2": ("http://localhost:50051/panel2", []),
    }


def test___start_panels___stop_panel_1_with_reset___enumerate_has_panel_2(
    fake_panel_channel: grpc.Channel,
) -> None:
    client = create_panel_client(fake_panel_channel)
    client.start_panel("panel1", "uri1", "python.exe")
    client.start_panel("panel2", "uri2", "python.exe")

    client.stop_panel("panel1", reset=True)

    assert client.enumerate_panels() == {
        "panel2": ("http://localhost:50051/panel2", []),
    }


def test___start_panels___stop_panel_1_without_reset___enumerate_has_both_panels(
    fake_panel_channel: grpc.Channel,
) -> None:
    client = create_panel_client(fake_panel_channel)
    client.start_panel("panel1", "uri1", "python.exe")
    client.start_panel("panel2", "uri2", "python.exe")

    client.stop_panel("panel1", reset=False)

    assert client.enumerate_panels() == {
        "panel1": ("", []),
        "panel2": ("http://localhost:50051/panel2", []),
    }


def test___get_unset_value___returns_not_found(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    response = client.get_value("panel1", "unset_id")

    assert response == (False, None)


def test___set_value___enumerate_panels_shows_value(
    fake_panel_channel: grpc.Channel,
) -> None:
    client = create_panel_client(fake_panel_channel)

    client.set_value("panel1", "val1", "value1", notify=False)

    assert client.enumerate_panels() == {"panel1": ("", ["val1"])}


def test___set_value___gets_value(fake_panel_channel: grpc.Channel) -> None:
    client = create_panel_client(fake_panel_channel)

    client.set_value("panel1", "val1", "value1", notify=False)

    assert client.get_value("panel1", "val1") == (True, "value1")


def create_panel_client(fake_panel_channel: grpc.Channel) -> PanelClient:
    return PanelClient(
        provided_interface="iface",
        service_class="svc",
        grpc_channel=fake_panel_channel,
    )
