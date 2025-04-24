from concurrent import futures
import grpc
import time
import google.protobuf.any_pb2 as any_pb2
from ni.pythonpanel.v1.python_panel_service_pb2 import ConnectRequest, ConnectResponse, DisconnectRequest, DisconnectResponse, GetValueRequest, GetValueResponse, SetValueRequest, SetValueResponse
from ni.pythonpanel.v1.python_panel_service_pb2_grpc import PythonPanelServiceServicer, add_PythonPanelServiceServicer_to_server

class FakePythonPanelService(PythonPanelServiceServicer):
    def Connect(self, request, context):
        # Basic implementation for testing
        print(f"Connecting to panel: {request.panel_id} at {request.panel_uri}")
        return ConnectResponse()

    def Disconnect(self, request, context):
        # Basic implementation for testing
        print(f"Disconnecting from panel: {request.panel_id}")
        return DisconnectResponse()

    def GetValue(self, request, context):
        # Basic implementation for testing
        print(f"Getting value for panel: {request.panel_id}, value_id: {request.value_id}")
        value = any_pb2.Any()  # Placeholder for actual value
        return GetValueResponse(value=value)

    def SetValue(self, request, context):
        # Basic implementation for testing
        print(f"Setting value for panel: {request.panel_id}, value_id: {request.value_id}, value: {request.value}")
        return SetValueResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_PythonPanelServiceServicer_to_server(FakePythonPanelService(), server)
    server.add_insecure_port('[::]:50051') # TODO: do we need to find a free port?
    server.start()
    print("Server is running on port 50051...")
    try:
        while True:
            time.sleep(86400)  # Keep the server running
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()