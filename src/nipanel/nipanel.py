import uuid
import grpc
from google.protobuf import any_pb2
import ni.pythonpanel.v1.python_panel_service_pb2 as python_panel_service_pb2
import ni.pythonpanel.v1.python_panel_service_pb2_grpc as python_panel_service_pb2_grpc

class NiPanel:
    """
    This class allows you to access controls on the panel
    """
    def __init__(self):
        self._stub = None # will be a PythonPanelServiceStub
        self.panel_uri = None
        self.panel_id = None

    def __enter__(self):
        self.connect()

    def __exit__(self):
        self.disconnect()

    @classmethod
    def streamlit_panel(cls, streamlit_script_path: str):
        """
        Create a panel using a streamlit script for the user interface

        Args:
            streamlit_script_path: The file path of the streamlit script

        Returns:
            NiPanel: A new panel associated with the streamlit script
        """
        panel = cls()
        panel.panel_uri = streamlit_script_path
        panel.panel_id = str(uuid.uuid4())
        return panel

    def connect(self): 
        """
        Connect to the panel and open it.
        """       
        # TODO: AB#3095680 - Use gRPC pool management from the Measurement Plugin SDK, create the _stub, and call _stub.Connect
        pass

    def disconnect(self):
        """
        Disconnect from the panel (does not close the panel).
        """
        # TODO: AB#3095680 - Use gRPC pool management from the Measurement Plugin SDK, call _stub.Disconnect
        pass

    def get_value(self, value_id: str):
        """
        Get the value for a control on the panel

        Args:
            value_id: The id of the value

        Returns:
            object: The value
        """
        # TODO: AB#3095681 - get the Any from _stub.GetValue and convert it to the correct type to return it
        return "placeholder value"

    def set_value(self, value_id: str, value):
        """
        Set the value for a control on the panel

        Args:
            value_id: The id of the value
            value: The value
        """
        # TODO: AB#3095681 - Convert the value to an Any and pass it to _stub.SetValue
        pass