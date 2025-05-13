

from grpc.aio import insecure_channel
from src.grpc.quota_pb2_grpc import AuthorizationStub, QuotaServiceStub


class GrpcConnection:

    def __init__(self):
        self.channel = None
        self._auth_stub = None
        self._quota_stub = None
        self._quota_stub_callback = self._stub_doesnt_exist(
            '_quota_stub', QuotaServiceStub, '_quota_stub_callback')
        self._auth_stub_callback = self._stub_doesnt_exist(
            '_auth_stub', AuthorizationStub, '_auth_stub_callback')

    @property
    def quota_stub(self) -> QuotaServiceStub:
        return self._quota_stub_callback()

    @property
    def auth_stub(self) -> AuthorizationStub:
        return self._auth_stub_callback()

    def _stub_doesnt_exist(self, stubname: str, Stub, callback_name):
        def wrapped(*args, **kwargs):
            stub = Stub(self.channel)
            setattr(self, stubname, stub)
            setattr(self, callback_name,
                    lambda *args: self._stub_exist(stubname))
            return stub
        return wrapped

    def _stub_exist(self, stubname: str):
        return getattr(self, stubname)

    async def on_startup(self):
        self.channel = await insecure_channel('localhost:50051').__aenter__()

    async def on_shutdown(self):
        await self.channel.__aexit__(None, None, None)


grpc_connection = GrpcConnection()
