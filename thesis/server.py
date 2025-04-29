import grpc

from .generated.quota_pb2_grpc import QuotaServiceServicer, add_QuotaServiceServicer_to_server
from .interceptors.logging_interceptor import LoggingInterceptor


class Server:
    def __init__(self, servicer: QuotaServiceServicer, port: int):
        self._server = grpc.aio.server(interceptors=[LoggingInterceptor()])
        add_QuotaServiceServicer_to_server(servicer, self._server)
        self._server.add_insecure_port(f"[::]:{port}")

    async def serve(self):
        await self._server.start()
        await self._server.wait_for_termination()
