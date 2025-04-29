import asyncio

import structlog

from .server import Server
from .servicers.quota_container import QuotaContainer
from .servicers.quota_servicer import QuotaServicer

log = structlog.get_logger()


async def main():
    await log.ainfo("Starting server")
    server = Server(QuotaServicer(), 50051)
    container = QuotaContainer()
    container.init_resources()
    container.wire(modules=[QuotaServicer])
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
