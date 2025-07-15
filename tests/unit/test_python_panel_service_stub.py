import pytest
from google.protobuf.any_pb2 import Any
from google.protobuf.wrappers_pb2 import StringValue
from ni.pythonpanel.v1.python_panel_service_pb2 import (
    StartPanelRequest,
    StopPanelRequest,
    EnumeratePanelsRequest,
    GetValueRequest,
    TryGetValueRequest,
    SetValueRequest,
)
from ni.pythonpanel.v1.python_panel_service_pb2_grpc import PythonPanelServiceStub


def test___start_panel___gets_response(python_panel_service_stub: PythonPanelServiceStub) -> None:
    request = StartPanelRequest(panel_id="test_panel", panel_script_path="path/to/panel")
    response = python_panel_service_stub.StartPanel(request)

    assert response.panel_url == "http://localhost:50051/test_panel"


def test___start_panel___stop_panel___gets_response(
    python_panel_service_stub: PythonPanelServiceStub,
) -> None:
    open_request = StartPanelRequest(panel_id="test_panel", panel_script_path="path/to/panel")
    python_panel_service_stub.StartPanel(open_request)

    request = StopPanelRequest(panel_id="test_panel", reset=False)
    response = python_panel_service_stub.StopPanel(request)

    assert response is not None  # Ensure response is returned


def test___enumerate_panels___gets_response(
    python_panel_service_stub: PythonPanelServiceStub,
) -> None:
    request = EnumeratePanelsRequest()
    response = python_panel_service_stub.EnumeratePanels(request)

    assert response is not None  # Ensure response is returned


def test___set_value___gets_response(
    python_panel_service_stub: PythonPanelServiceStub,
) -> None:
    test_value = Any()
    test_value.Pack(StringValue(value="test_value"))
    request = SetValueRequest(panel_id="test_panel", value_id="test_value", value=test_value)
    response = python_panel_service_stub.SetValue(request)

    assert response is not None  # Ensure response is returned


def test___set_value___get_value___gets_response(
    python_panel_service_stub: PythonPanelServiceStub,
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
    python_panel_service_stub: PythonPanelServiceStub,
) -> None:
    request = GetValueRequest(panel_id="test_panel", value_id="test_value")
    with pytest.raises(Exception):
        python_panel_service_stub.GetValue(request)


def test___set_value___try_get_value___gets_response(
    python_panel_service_stub: PythonPanelServiceStub,
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
    python_panel_service_stub: PythonPanelServiceStub,
) -> None:
    request = TryGetValueRequest(panel_id="test_panel", value_id="test_value")
    response = python_panel_service_stub.TryGetValue(request)

    assert response is not None  # Ensure response is returned
    assert response.HasField("value") is False  # Ensure no value is returned
