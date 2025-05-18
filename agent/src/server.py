import grpc
from src.grpc.quota_pb2_grpc import (
    add_ResourcesServicer_to_server,
)
from src.interceptors.logging_interceptor import LoggingInterceptor
from src.servicers.resource_servicer import ResourcesServicer


class Server:
    def __init__(self, port: int):
        self._server = grpc.aio.server(interceptors=[LoggingInterceptor()])
        add_ResourcesServicer_to_server(ResourcesServicer(), self._server)
        self._server.add_insecure_port(f"[::]:{port}")

    async def serve(self):
        await self._server.start()
        await self._server.wait_for_termination()
