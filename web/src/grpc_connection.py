

from grpc.aio import insecure_channel


class GrpcConnection:

    def __init__(self):
        self.channel = None

    async def on_startup(self):
        self.channel = await insecure_channel('localhost:50051').__aenter__()

    async def on_shutdown(self):
        await self.channel.__aexit__(None, None, None)


grpc_connection = GrpcConnection()
