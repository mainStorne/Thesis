import grpc
from src.grpc.quota_pb2_grpc import (
    AuthorizationServicer,
    QuotaServiceServicer,
    add_AuthorizationServicer_to_server,
    add_QuotaServiceServicer_to_server,
)
from src.interceptors.logging_interceptor import LoggingInterceptor
from src.repos.docker_repo import docker_repo


class Server:
    def __init__(self, authorization: AuthorizationServicer, quota: QuotaServiceServicer, port: int):
        self._server = grpc.aio.server(interceptors=[LoggingInterceptor()])
        add_AuthorizationServicer_to_server(authorization, self._server)
        add_QuotaServiceServicer_to_server(quota, self._server)
        self._server.add_insecure_port(f"[::]:{port}")

    async def serve(self):
        await docker_repo.init()
        await self._server.start()
        await self._server.wait_for_termination()
