from google.protobuf.any_pb2 import Any
from ni.pythonpanel.v1.python_panel_service_pb2 import (
    ConnectRequest,
    DisconnectRequest,
    GetValueRequest,
    SetValueRequest,
)
from ni.pythonpanel.v1.python_panel_service_pb2_grpc import PythonPanelServiceStub


def test___connect___gets_response(fake_python_panel_service_stub: PythonPanelServiceStub) -> None:
    request = ConnectRequest(panel_id="test_panel", panel_uri="path/to/panel")
    response = fake_python_panel_service_stub.Connect(request)
    assert response is not None  # Ensure response is returned


def test___disconnect___gets_response(
    fake_python_panel_service_stub: PythonPanelServiceStub,
) -> None:
    request = DisconnectRequest(panel_id="test_panel")
    response = fake_python_panel_service_stub.Disconnect(request)
    assert response is not None  # Ensure response is returned


def test___get_value___gets_response(
    fake_python_panel_service_stub: PythonPanelServiceStub,
) -> None:
    request = GetValueRequest(panel_id="test_panel", value_id="test_value")
    response = fake_python_panel_service_stub.GetValue(request)
    assert response is not None  # Ensure response is returned
    assert isinstance(response.value, Any)  # Ensure the value is of type `Any`


def test___set_value___gets_response(
    fake_python_panel_service_stub: PythonPanelServiceStub,
) -> None:
    value = Any()
    value.value = b"test_data"
    request = SetValueRequest(panel_id="test_panel", value_id="test_value", value=value)
    response = fake_python_panel_service_stub.SetValue(request)
    assert response is not None  # Ensure response is returned
