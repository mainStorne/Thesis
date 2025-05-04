import asyncio

import structlog

from .server import Server
from .servicers.quota_servicer import QuotaServicer

log = structlog.get_logger()


async def main():
    await log.ainfo("Starting server")
    server = Server(QuotaServicer(), 50051)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
