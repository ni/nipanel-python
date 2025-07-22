import pytest
from google.protobuf.any_pb2 import Any
from google.protobuf.wrappers_pb2 import StringValue
from ni.panels.v1.panel_service_pb2 import (
    StartPanelRequest,
    StopPanelRequest,
    EnumeratePanelsRequest,
    GetValueRequest,
    TryGetValueRequest,
    SetValueRequest,
)
from ni.panels.v1.panel_service_pb2_grpc import PanelServiceStub
from ni.panels.v1.streamlit_panel_configuration_pb2 import StreamlitPanelConfiguration


def test___start_panel___gets_response(python_panel_service_stub: PanelServiceStub) -> None:
    configuration = StreamlitPanelConfiguration(panel_script_path="path/to/panel.py")
    configuration_any = Any()
    configuration_any.Pack(configuration)
    request = StartPanelRequest(panel_id="test_panel", panel_configuration=configuration_any)
    response = python_panel_service_stub.StartPanel(request)

    assert response.panel_uri == "http://localhost:50051/test_panel"


def test___start_panel___stop_panel___gets_response(
    python_panel_service_stub: PanelServiceStub,
) -> None:
    configuration = StreamlitPanelConfiguration(panel_script_path="path/to/panel.py")
    configuration_any = Any()
    configuration_any.Pack(configuration)
    start_request = StartPanelRequest(panel_id="test_panel", panel_configuration=configuration_any)
    python_panel_service_stub.StartPanel(start_request)

    stop_request = StopPanelRequest(panel_id="test_panel", reset=False)
    response = python_panel_service_stub.StopPanel(stop_request)

    assert response is not None  # Ensure response is returned


def test___enumerate_panels___gets_response(
    python_panel_service_stub: PanelServiceStub,
) -> None:
    request = EnumeratePanelsRequest()
    response = python_panel_service_stub.EnumeratePanels(request)

    assert response is not None  # Ensure response is returned


def test___set_value___gets_response(
    python_panel_service_stub: PanelServiceStub,
) -> None:
    test_value = Any()
    test_value.Pack(StringValue(value="test_value"))
    request = SetValueRequest(panel_id="test_panel", value_id="test_value", value=test_value)
    response = python_panel_service_stub.SetValue(request)

    assert response is not None  # Ensure response is returned


def test___set_value___get_value___gets_response(
    python_panel_service_stub: PanelServiceStub,
) -> None:
    test_value = Any()
    test_value.Pack(StringValue(value="test_value"))
    set_request = SetValueRequest(panel_id="test_panel", value_id="test_value", value=test_value)
    python_panel_service_stub.SetValue(set_request)

    request = GetValueRequest(panel_id="test_panel", value_id="test_value")
    response = python_panel_service_stub.GetValue(request)

    assert response is not None  # Ensure response is returned
    assert response.value == test_value  # Ensure the value is correct


def test___no_value___get_value___raises_exception(
    python_panel_service_stub: PanelServiceStub,
) -> None:
    request = GetValueRequest(panel_id="test_panel", value_id="test_value")
    with pytest.raises(Exception):
        python_panel_service_stub.GetValue(request)


def test___set_value___try_get_value___gets_response(
    python_panel_service_stub: PanelServiceStub,
) -> None:
    test_value = Any()
    test_value.Pack(StringValue(value="test_value"))
    set_request = SetValueRequest(panel_id="test_panel", value_id="test_value", value=test_value)
    python_panel_service_stub.SetValue(set_request)

    request = TryGetValueRequest(panel_id="test_panel", value_id="test_value")
    response = python_panel_service_stub.TryGetValue(request)

    assert response is not None  # Ensure response is returned
    assert response.value == test_value  # Ensure the value is correct


def test___no_value___try_get_value___gets_no_value(
    python_panel_service_stub: PanelServiceStub,
) -> None:
    request = TryGetValueRequest(panel_id="test_panel", value_id="test_value")
    response = python_panel_service_stub.TryGetValue(request)

    assert response is not None  # Ensure response is returned
    assert response.HasField("value") is False  # Ensure no value is returned
