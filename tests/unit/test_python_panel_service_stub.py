from google.protobuf.any_pb2 import Any
from google.protobuf.wrappers_pb2 import StringValue
from ni.pythonpanel.v1.python_panel_service_pb2 import (
    OpenPanelRequest,
    ClosePanelRequest,
    EnumeratePanelsRequest,
    GetValueRequest,
    SetValueRequest,
)
from ni.pythonpanel.v1.python_panel_service_pb2_grpc import PythonPanelServiceStub


def test___open_panel___gets_response(python_panel_service_stub: PythonPanelServiceStub) -> None:
    request = OpenPanelRequest(panel_id="test_panel", panel_uri="path/to/panel")
    response = python_panel_service_stub.OpenPanel(request)

    assert response is not None  # Ensure response is returned


def test___open_panel___close_panel___gets_response(
    python_panel_service_stub: PythonPanelServiceStub,
) -> None:
    open_request = OpenPanelRequest(panel_id="test_panel", panel_uri="path/to/panel")
    python_panel_service_stub.OpenPanel(open_request)

    request = ClosePanelRequest(panel_id="test_panel", reset=False)
    response = python_panel_service_stub.ClosePanel(request)

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
