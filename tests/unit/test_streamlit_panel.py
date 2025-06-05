import grpc
import pytest

import tests.types as test_types
from nipanel import StreamlitPanel, StreamlitPanelValueAccessor
from tests.utils._fake_python_panel_service import FakePythonPanelService


def test___panel___has_panel_id_and_panel_script_path(fake_panel_channel: grpc.Channel) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    assert panel.panel_id == "my_panel"
    assert panel.panel_script_path == "path/to/script"


def test___different_panels___have_different_panel_ids_and_panel_script_paths(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel1 = StreamlitPanel("panel1", "path/to/script1", grpc_channel=fake_panel_channel)
    panel2 = StreamlitPanel("panel2", "path/to/script2", grpc_channel=fake_panel_channel)

    assert panel1.panel_id == "panel1"
    assert panel2.panel_id == "panel2"
    assert panel1._panel_script_path == "path/to/script1"
    assert panel2._panel_script_path == "path/to/script2"
    assert panel1._panel_client != panel2._panel_client


def test___panel___set_value___gets_same_value(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

    value_id = "test_id"
    string_value = "test_value"
    panel.set_value(value_id, string_value)

    assert panel.get_value(value_id) == string_value


def test___panel___panel_set_value___accessor_gets_same_value(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    accessor = StreamlitPanelValueAccessor("my_panel", grpc_channel=fake_panel_channel)

    value_id = "test_id"
    string_value = "test_value"
    panel.set_value(value_id, string_value)

    assert accessor.get_value(value_id) == string_value


def test___panel___accessor_set_value___panel_gets_same_value(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    accessor = StreamlitPanelValueAccessor("my_panel", grpc_channel=fake_panel_channel)

    value_id = "test_id"
    string_value = "test_value"
    accessor.set_value(value_id, string_value)

    assert panel.get_value(value_id) == string_value


def test___first_start_will_fail___start_panel___panel_is_functional(
    fake_python_panel_service: FakePythonPanelService,
    fake_panel_channel: grpc.Channel,
) -> None:
    """Test that panel.start_panel() will automatically retry once."""
    service = fake_python_panel_service
    # Simulate a failure on the first attempt
    service.servicer.fail_next_start_panel()

    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

    value_id = "test_id"
    string_value = "test_value"
    panel.set_value(value_id, string_value)
    assert panel.get_value(value_id) == string_value
    assert panel._panel_client.enumerate_panels() == {
        "my_panel": ("http://localhost:50051/my_panel", [value_id])
    }


def test___panel___set_value___sets_value(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

    value_id = "test_id"
    string_value = "test_value"
    panel.set_value(value_id, string_value)

    assert panel._panel_client.enumerate_panels() == {
        "my_panel": ("http://localhost:50051/my_panel", [value_id])
    }


def test___panel___get_unset_value___raises_exception(
    fake_panel_channel: grpc.Channel,
) -> None:
    """Test that get_value() raises an exception for an unset value."""
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

    value_id = "test_id"
    with pytest.raises(grpc.RpcError):
        panel.get_value(value_id)


def test___panel___set_value___gets_value(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

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
    fake_panel_channel: grpc.Channel,
    value_payload: object,
) -> None:
    """Test that set_value() and get_value() work for builtin scalar types."""
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

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
    fake_panel_channel: grpc.Channel,
    value_payload: object,
) -> None:
    """Test that set_value() raises for unsupported types."""
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

    value_id = "test_id"
    with pytest.raises(TypeError):
        panel.set_value(value_id, value_payload)


@pytest.mark.parametrize(
    "value_payload",
    [
        # Bool
        list(x % 2 == 0 for x in range(0, 10)),
        set(x % 2 == 0 for x in range(10, 20)),
        frozenset(x % 2 == 0 for x in range(20, 30)),
        tuple(x % 2 == 0 for x in range(30, 40)),
        # Bytes
        list(bytes(x) for x in range(0, 10)),
        set(bytes(x) for x in range(10, 20)),
        frozenset(bytes(x) for x in range(20, 30)),
        tuple(bytes(x) for x in range(30, 40)),
        # Float
        list(float(x) for x in range(0, 10)),
        set(float(x) for x in range(10, 20)),
        frozenset(float(x) for x in range(20, 30)),
        tuple(float(x) for x in range(30, 40)),
        # Integer
        list(range(0, 10)),
        set(range(10, 20)),
        frozenset(range(20, 30)),
        tuple(range(30, 40)),
        # String
        list(str(x) for x in range(0, 10)),
        set(str(x) for x in range(10, 20)),
        frozenset(str(x) for x in range(20, 30)),
        tuple(str(x) for x in range(30, 40)),
        # Enum canaries
        list(x for x in test_types.MixinIntEnum),
        set(x for x in test_types.MixinIntEnum),
        frozenset(x for x in test_types.MixinIntEnum),
        tuple(x for x in test_types.MixinIntEnum),
        list(x for x in test_types.MixinStrEnum),
        set(x for x in test_types.MixinStrEnum),
        frozenset(x for x in test_types.MixinStrEnum),
        tuple(x for x in test_types.MixinStrEnum),
    ],
)
def test___sequence_of_builtin_type___set_value___gets_same_value(
    fake_panel_channel: grpc.Channel,
    value_payload: object,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

    value_id = "test_id"
    panel.set_value(value_id, value_payload)

    received_value = panel.get_value(value_id)
    assert list(received_value) == list(value_payload)  # type: ignore [call-overload]


def test___panel___panel_is_running_and_in_memory(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

    assert is_panel_in_memory(panel)
    assert is_panel_running(panel)


def is_panel_in_memory(panel: StreamlitPanel) -> bool:
    return panel.panel_id in panel._panel_client.enumerate_panels().keys()


def is_panel_running(panel: StreamlitPanel) -> bool:
    return panel._panel_client.enumerate_panels()[panel.panel_id][0] != ""
