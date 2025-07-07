import enum
from datetime import datetime

import grpc
import pytest
from typing_extensions import assert_type

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


def test___panel___set_value___notifies(
    fake_python_panel_service: FakePythonPanelService,
    fake_panel_channel: grpc.Channel,
) -> None:
    service = fake_python_panel_service
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    assert service.servicer.notification_count == 0

    panel.set_value("value_id", "string_value")

    assert service.servicer.notification_count == 1


def test___accessor___set_value___does_not_notify(
    fake_python_panel_service: FakePythonPanelService,
    fake_panel_channel: grpc.Channel,
) -> None:
    service = fake_python_panel_service
    accessor = StreamlitPanelValueAccessor("my_panel", grpc_channel=fake_panel_channel)
    assert service.servicer.notification_count == 0

    accessor.set_value("value_id", "string_value")

    assert service.servicer.notification_count == 0


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


def test___panel___get_unset_value_with_no_default___raises_exception(
    fake_panel_channel: grpc.Channel,
) -> None:
    """Test that get_value() raises an exception for an unset value."""
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

    value_id = "test_id"
    with pytest.raises(KeyError):
        panel.get_value(value_id)


def test___panel___set_value___gets_value(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

    value_id = "test_id"
    string_value = "test_value"
    panel.set_value(value_id, string_value)

    assert panel.get_value(value_id) == string_value


def test___panel___set_value___get_value_ignores_default(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

    value_id = "test_id"
    string_value = "test_value"
    panel.set_value(value_id, string_value)

    assert panel.get_value(value_id, "default") == string_value


def test___no_set_value___get_value_returns_default(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

    assert panel.get_value("missing_string", "default") == "default"
    assert panel.get_value("missing_int", 123) == 123
    assert panel.get_value("missing_float", 1.23) == 1.23
    assert panel.get_value("missing_bool", True) is True
    assert panel.get_value("missing_list", [1, 2, 3]) == [1, 2, 3]
    assert_type(panel.get_value("missing_string", "default"), str)
    assert_type(panel.get_value("missing_int", 123), int)
    assert_type(panel.get_value("missing_float", 1.23), float)
    assert_type(panel.get_value("missing_bool", True), bool)
    assert_type(panel.get_value("missing_list", [1, 2, 3]), list[int])


def test___set_string_type___get_value_with_string_default___returns_string_type(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    value_id = "test_id"
    string_value = "test_value"
    panel.set_value(value_id, string_value)

    value = panel.get_value(value_id, "")

    assert_type(value, str)
    assert value == string_value


def test___set_int_type___get_value_with_int_default___returns_int_type(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    value_id = "test_id"
    int_value = 10
    panel.set_value(value_id, int_value)

    value = panel.get_value(value_id, 0)

    assert_type(value, int)
    assert value == int_value


def test___set_bool_type___get_value_with_bool_default___returns_bool_type(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    value_id = "test_id"
    bool_value = True
    panel.set_value(value_id, bool_value)

    value = panel.get_value(value_id, False)

    assert_type(value, bool)
    assert value is bool_value


def test___set_string_type___get_value_with_int_default___raises_exception(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    value_id = "test_id"
    string_value = "test_value"
    panel.set_value(value_id, string_value)

    with pytest.raises(TypeError):
        panel.get_value(value_id, 0)


def test___set_int_type___get_value_with_bool_default___raises_exception(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    value_id = "test_id"
    int_value = 10
    panel.set_value(value_id, int_value)

    with pytest.raises(TypeError):
        panel.get_value(value_id, False)


def test___set_string_enum_type___get_value_with_int_enum_default___raises_exception(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    value_id = "test_id"
    panel.set_value(value_id, test_types.MyStrEnum.VALUE3)

    with pytest.raises(ValueError):
        panel.get_value(value_id, test_types.MyIntEnum.VALUE10)


@pytest.mark.parametrize(
    "value_payload",
    [
        "firstname bunchanumbers",
        42,
        3.14,
        True,
        b"robotext",
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
        test_types.MyIntFlags.VALUE1 | test_types.MyIntFlags.VALUE4,
        test_types.MyIntableFlags.VALUE16 | test_types.MyIntableFlags.VALUE32,
        test_types.MyIntEnum.VALUE20,
        test_types.MyIntableEnum.VALUE200,
        test_types.MyStrEnum.VALUE3,
        test_types.MyStringableEnum.VALUE2,
        test_types.MixinIntEnum.VALUE33,
        test_types.MixinStrEnum.VALUE11,
        test_types.MyMixedEnum.VALUE2,
    ],
)
def test___enum_type___set_value___gets_same_value(
    fake_panel_channel: grpc.Channel,
    value_payload: enum.Enum,
) -> None:
    """Test that set_value() and get_value() work for builtin scalar types."""
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

    value_id = "test_id"
    panel.set_value(value_id, value_payload)

    # without providing a default value, get_value will return the raw value, not the enum
    assert panel.get_value(value_id) == value_payload.value


@pytest.mark.parametrize(
    "value_payload",
    [
        datetime.now(),
        lambda x: x + 1,
        [1, "string"],
        ["string", []],
        (42, "hello", 3.14, b"bytes"),
        set([1, "mixed", True]),
        (i for i in range(5)),
        {
            "key1": [1, 2, 3],
            "key2": {"nested": True, "values": [4.5, 6.7]},
        },
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


def test___set_int_enum_value___get_value___returns_int_enum(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    value_id = "test_id"
    enum_value = test_types.MyIntEnum.VALUE20
    panel.set_value(value_id, enum_value)

    retrieved_value = panel.get_value(value_id, test_types.MyIntEnum.VALUE10)

    assert_type(retrieved_value, test_types.MyIntEnum)
    assert retrieved_value is test_types.MyIntEnum.VALUE20
    assert retrieved_value.value == enum_value.value
    assert retrieved_value.name == enum_value.name


def test___set_intable_enum_value___get_value___returns_intable_enum(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    value_id = "test_id"
    enum_value = test_types.MyIntableEnum.VALUE200
    panel.set_value(value_id, enum_value)

    retrieved_value = panel.get_value(value_id, test_types.MyIntableEnum.VALUE100)

    assert_type(retrieved_value, test_types.MyIntableEnum)
    assert retrieved_value is test_types.MyIntableEnum.VALUE200
    assert retrieved_value.value == enum_value.value
    assert retrieved_value.name == enum_value.name


def test___set_string_enum_value___get_value___returns_string_enum(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    value_id = "test_id"
    enum_value = test_types.MyStrEnum.VALUE3
    panel.set_value(value_id, enum_value)

    retrieved_value = panel.get_value(value_id, test_types.MyStrEnum.VALUE1)

    assert_type(retrieved_value, test_types.MyStrEnum)
    assert retrieved_value is test_types.MyStrEnum.VALUE3
    assert retrieved_value.value == enum_value.value
    assert retrieved_value.name == enum_value.name


def test___set_stringable_enum_value___get_value___returns_stringable_enum(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    value_id = "test_id"
    enum_value = test_types.MyStringableEnum.VALUE3
    panel.set_value(value_id, enum_value)

    retrieved_value = panel.get_value(value_id, test_types.MyStringableEnum.VALUE1)

    assert_type(retrieved_value, test_types.MyStringableEnum)
    assert retrieved_value is test_types.MyStringableEnum.VALUE3
    assert retrieved_value.value == enum_value.value
    assert retrieved_value.name == enum_value.name


def test___set_mixed_enum_value___get_value___returns_mixed_enum(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    value_id = "test_id"
    enum_value = test_types.MyMixedEnum.VALUE2
    panel.set_value(value_id, enum_value)

    retrieved_value = panel.get_value(value_id, test_types.MyMixedEnum.VALUE1)

    assert_type(retrieved_value, test_types.MyMixedEnum)
    assert retrieved_value is test_types.MyMixedEnum.VALUE2
    assert retrieved_value.value == enum_value.value
    assert retrieved_value.name == enum_value.name


def test___set_int_flags_value___get_value___returns_int_flags(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    value_id = "test_id"
    flags_value = test_types.MyIntFlags.VALUE1 | test_types.MyIntFlags.VALUE4
    panel.set_value(value_id, flags_value)

    retrieved_value = panel.get_value(value_id, test_types.MyIntFlags.VALUE2)

    assert_type(retrieved_value, test_types.MyIntFlags)
    assert retrieved_value == (test_types.MyIntFlags.VALUE1 | test_types.MyIntFlags.VALUE4)
    assert retrieved_value.value == flags_value.value


def test___set_intable_flags_value___get_value___returns_intable_flags(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)
    value_id = "test_id"
    flags_value = test_types.MyIntableFlags.VALUE16 | test_types.MyIntableFlags.VALUE32
    panel.set_value(value_id, flags_value)

    retrieved_value = panel.get_value(value_id, test_types.MyIntableFlags.VALUE8)

    assert_type(retrieved_value, test_types.MyIntableFlags)
    assert retrieved_value is test_types.MyIntableFlags.VALUE16 | test_types.MyIntableFlags.VALUE32
    assert retrieved_value.value == flags_value.value
    assert retrieved_value.name == flags_value.name


def test___panel___panel_is_running_and_in_memory(
    fake_panel_channel: grpc.Channel,
) -> None:
    panel = StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

    assert is_panel_in_memory(panel)
    assert is_panel_running(panel)


def test___panel___python_path_is_in_venv(
    fake_python_panel_service: FakePythonPanelService,
    fake_panel_channel: grpc.Channel,
) -> None:
    StreamlitPanel("my_panel", "path/to/script", grpc_channel=fake_panel_channel)

    assert ".venv" in fake_python_panel_service.servicer.python_path


def is_panel_in_memory(panel: StreamlitPanel) -> bool:
    return panel.panel_id in panel._panel_client.enumerate_panels().keys()


def is_panel_running(panel: StreamlitPanel) -> bool:
    return panel._panel_client.enumerate_panels()[panel.panel_id][0] != ""
