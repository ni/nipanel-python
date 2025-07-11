import grpc

from nipanel import StreamlitPanelValueAccessor
from tests.types import MyIntEnum
from tests.utils._fake_python_panel_service import FakePythonPanelService


def test___no_previous_value___set_value_if_changed___sets_value(
    fake_panel_channel: grpc.Channel,
) -> None:
    accessor = StreamlitPanelValueAccessor("panel_id", grpc_channel=fake_panel_channel)

    accessor.set_value_if_changed("test_id", "test_value")

    assert accessor.get_value("test_id") == "test_value"


def test___set_value_if_changed___set_same_value___does_not_set_value_again(
    fake_panel_channel: grpc.Channel,
    fake_python_panel_service: FakePythonPanelService,
) -> None:
    accessor = StreamlitPanelValueAccessor("panel_id", grpc_channel=fake_panel_channel)
    accessor.set_value_if_changed("test_id", "test_value")
    initial_set_count = fake_python_panel_service.servicer.set_count

    accessor.set_value_if_changed("test_id", "test_value")

    assert fake_python_panel_service.servicer.set_count == initial_set_count
    assert accessor.get_value("test_id") == "test_value"


def test___set_value_if_changed___set_different_value___sets_new_value(
    fake_panel_channel: grpc.Channel,
) -> None:
    accessor = StreamlitPanelValueAccessor("panel_id", grpc_channel=fake_panel_channel)
    accessor.set_value_if_changed("test_id", "test_value")

    accessor.set_value_if_changed("test_id", "new_value")

    assert accessor.get_value("test_id") == "new_value"


def test___set_value_if_changed___different_value_ids___tracks_separately(
    fake_panel_channel: grpc.Channel,
) -> None:
    accessor = StreamlitPanelValueAccessor("panel_id", grpc_channel=fake_panel_channel)
    accessor.set_value_if_changed("id1", "value1")
    accessor.set_value_if_changed("id2", "value2")

    accessor.set_value_if_changed("id1", "value1")
    accessor.set_value_if_changed("id2", "new_value2")

    assert accessor.get_value("id1") == "value1"
    assert accessor.get_value("id2") == "new_value2"


def test___set_value_if_changed_with_list_value___set_same_value___does_not_set_value_again(
    fake_panel_channel: grpc.Channel,
    fake_python_panel_service: FakePythonPanelService,
) -> None:
    accessor = StreamlitPanelValueAccessor("panel_id", grpc_channel=fake_panel_channel)
    accessor.set_value_if_changed("test_id", [1, 2, 3])
    initial_set_count = fake_python_panel_service.servicer.set_count

    accessor.set_value_if_changed("test_id", [1, 2, 3])

    assert fake_python_panel_service.servicer.set_count == initial_set_count
    assert accessor.get_value("test_id") == [1, 2, 3]


def test___set_value_if_changed_with_list_value___set_different_value___sets_new_value(
    fake_panel_channel: grpc.Channel,
    fake_python_panel_service: FakePythonPanelService,
) -> None:
    accessor = StreamlitPanelValueAccessor("panel_id", grpc_channel=fake_panel_channel)
    accessor.set_value_if_changed("test_id", [1, 2, 3])
    initial_set_count = fake_python_panel_service.servicer.set_count

    accessor.set_value_if_changed("test_id", [1, 2, 4])

    assert fake_python_panel_service.servicer.set_count > initial_set_count
    assert accessor.get_value("test_id") == [1, 2, 4]


def test___set_value_if_changed_with_enum_value___set_same_value___does_not_set_value_again(
    fake_panel_channel: grpc.Channel,
    fake_python_panel_service: FakePythonPanelService,
) -> None:
    accessor = StreamlitPanelValueAccessor("panel_id", grpc_channel=fake_panel_channel)
    accessor.set_value_if_changed("test_id", MyIntEnum.VALUE20)
    initial_set_count = fake_python_panel_service.servicer.set_count

    accessor.set_value_if_changed("test_id", MyIntEnum.VALUE20)

    assert fake_python_panel_service.servicer.set_count == initial_set_count
    assert accessor.get_value("test_id") == 20  # Enums are stored as their values


def test___set_value_if_changed_with_enum_value___set_different_value___sets_new_value(
    fake_panel_channel: grpc.Channel,
    fake_python_panel_service: FakePythonPanelService,
) -> None:
    accessor = StreamlitPanelValueAccessor("panel_id", grpc_channel=fake_panel_channel)
    accessor.set_value_if_changed("test_id", MyIntEnum.VALUE20)
    initial_set_count = fake_python_panel_service.servicer.set_count

    accessor.set_value_if_changed("test_id", MyIntEnum.VALUE30)

    assert fake_python_panel_service.servicer.set_count > initial_set_count
    assert accessor.get_value("test_id") == 30  # New enum value should be set
