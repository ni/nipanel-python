import grpc

from tests.utils._fake_panel import FakePanel


def test___panel___has_panel_id_and_panel_uri() -> None:
    panel = FakePanel(0, "my_panel", "path/to/script")
    assert panel.panel_id == "my_panel"
    assert panel.panel_uri == "path/to/script"


def test___connected_panel___set_value___gets_same_value(
    fake_python_panel_service: tuple[grpc.Server, int],
) -> None:
    _, port = fake_python_panel_service
    panel = FakePanel(port, "my_panel", "path/to/script")
    panel.connect()

    panel.set_value("test_id", "test_value")

    # TODO: AB#3095681 - change asserted value to test_value
    assert panel.get_value("test_id") == "placeholder value"
    panel.disconnect()


def test___with_panel___set_value___gets_same_value(
    fake_python_panel_service: tuple[grpc.Server, int],
) -> None:
    _, port = fake_python_panel_service
    with FakePanel(port, "my_panel", "path/to/script") as panel:
        panel.set_value("test_id", "test_value")

        # TODO: AB#3095681 - change asserted value to test_value
        assert panel.get_value("test_id") == "placeholder value"
