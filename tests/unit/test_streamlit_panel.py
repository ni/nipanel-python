import grpc
import pytest

import tests.types as test_types
from nipanel._streamlit_panel import StreamlitPanel
from tests.utils._fake_python_panel_service import FakePythonPanelService


def test___panel___has_panel_id_and_panel_uri() -> None:
    panel = StreamlitPanel("my_panel", "path/to/script")
    assert panel.panel_id == "my_panel"
    assert panel.panel_uri == "path/to/script"


def test___opened_panel___set_value___gets_same_value(
    grpc_channel_for_fake_panel_service: grpc.Channel,
) -> None:
    channel = grpc_channel_for_fake_panel_service
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=channel)
    panel.open_panel()

    value_id = "test_id"
    string_value = "test_value"
    panel.set_value(value_id, string_value)

    assert panel.get_value(value_id) == string_value


def test___first_open_panel_fails___open_panel___gets_value(
    fake_python_panel_service: FakePythonPanelService,
    grpc_channel_for_fake_panel_service: grpc.Channel,
) -> None:
    """Test that panel.open_panel() will automatically retry once."""
    channel = grpc_channel_for_fake_panel_service
    service = fake_python_panel_service
    # Simulate a failure on the first attempt
    service.servicer.fail_next_open_panel()
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=channel)

    panel.open_panel()

    value_id = "test_id"
    string_value = "test_value"
    panel.set_value(value_id, string_value)
    assert panel.get_value(value_id) == string_value


def test___unopened_panel___set_value___sets_value(
    grpc_channel_for_fake_panel_service: grpc.Channel,
) -> None:
    """Test that set_value() succeeds before the user opens the panel."""
    channel = grpc_channel_for_fake_panel_service
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=channel)

    value_id = "test_id"
    string_value = "test_value"
    panel.set_value(value_id, string_value)

    assert panel.get_value(value_id) == string_value


def test___unopened_panel___get_unset_value___raises_exception(
    grpc_channel_for_fake_panel_service: grpc.Channel,
) -> None:
    """Test that get_value() raises an exception for an unset value."""
    channel = grpc_channel_for_fake_panel_service
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=channel)

    value_id = "test_id"
    with pytest.raises(grpc.RpcError):
        panel.get_value(value_id)


def test___unopened_panel___get_set_value___gets_value(
    grpc_channel_for_fake_panel_service: grpc.Channel,
) -> None:
    """Test that get_value() succeeds for a set value before the user opens the panel."""
    channel = grpc_channel_for_fake_panel_service
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=channel)

    value_id = "test_id"
    string_value = "test_value"
    panel.set_value(value_id, string_value)

    assert panel.get_value(value_id) == string_value


@pytest.mark.parametrize(
    "value_payload",
    [
        "firstname bunchanumbers",
        42,
        3.14,
        True,
        b"robotext",
        test_types.MyIntFlags.VALUE1 | test_types.MyIntFlags.VALUE4,
        test_types.MyIntEnum.VALUE20,
        test_types.MyStrEnum.VALUE3,
        test_types.MixinIntEnum.VALUE33,
        test_types.MixinStrEnum.VALUE11,
    ],
)
def test___builtin_scalar_type___set_value___gets_same_value(
    grpc_channel_for_fake_panel_service: grpc.Channel,
    value_payload: object,
) -> None:
    """Test that set_value() and get_value() work for builtin scalar types."""
    channel = grpc_channel_for_fake_panel_service
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=channel)

    value_id = "test_id"
    panel.set_value(value_id, value_payload)

    assert panel.get_value(value_id) == value_payload


@pytest.mark.parametrize(
    "value_payload",
    [
        test_types.MyEnum.VALUE300,
        test_types.MyFlags.VALUE8 | test_types.MyFlags.VALUE16,
    ],
)
def test___unsupported_type___set_value___raises(
    grpc_channel_for_fake_panel_service: grpc.Channel,
    value_payload: object,
) -> None:
    """Test that set_value() raises for unsupported types."""
    channel = grpc_channel_for_fake_panel_service
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=channel)

    value_id = "test_id"
    with pytest.raises(TypeError):
        panel.set_value(value_id, value_payload)
