import pytest

from tests.utils._fake_python_panel_servicer import FakePythonPanelServicer
from tests.utils._port_panel import PortPanel


def test___panel___has_panel_id_and_panel_uri() -> None:
    panel = PortPanel(0, "my_panel", "path/to/script")
    assert panel.panel_id == "my_panel"
    assert panel.panel_uri == "path/to/script"


def test___connected_panel___set_value___gets_same_value(
    fake_python_panel_service: tuple[FakePythonPanelServicer, int],
) -> None:
    _, port = fake_python_panel_service
    panel = PortPanel(port, "my_panel", "path/to/script")
    panel.connect()

    panel.set_value("test_id", "test_value")

    # TODO: AB#3095681 - change asserted value to test_value
    assert panel.get_value("test_id") == "placeholder value"
    panel.disconnect()


def test___with_panel___set_value___gets_same_value(
    fake_python_panel_service: tuple[FakePythonPanelServicer, int],
) -> None:
    _, port = fake_python_panel_service
    with PortPanel(port, "my_panel", "path/to/script") as panel:
        panel.set_value("test_id", "test_value")

        # TODO: AB#3095681 - change asserted value to test_value
        assert panel.get_value("test_id") == "placeholder value"


def test___new_panel___disconnect___raises_runtime_error(
    fake_python_panel_service: tuple[FakePythonPanelServicer, int],
) -> None:
    _, port = fake_python_panel_service
    panel = PortPanel(port, "my_panel", "path/to/script")

    with pytest.raises(RuntimeError):
        panel.disconnect()


def test___first_connect_fails___connect___gets_value(
    fake_python_panel_service: tuple[FakePythonPanelServicer, int],
) -> None:
    """Test that panel.connect() will automatically retry once."""
    servicer, port = fake_python_panel_service
    # Simulate a failure on the first connect attempt
    servicer.fail_next_connect()
    panel = PortPanel(port, "my_panel", "path/to/script")

    panel.connect()

    panel.set_value("test_id", "test_value")
    # TODO: AB#3095681 - change asserted value to test_value
    assert panel.get_value("test_id") == "placeholder value"
    panel.disconnect()
