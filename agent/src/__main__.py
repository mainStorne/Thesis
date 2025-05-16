import asyncio

import structlog

from src.server import Server
from src.servicers.auth_servicer import AuthorizationServicer
from src.servicers.quota_servicer import QuotaServicer

log = structlog.get_logger()


async def main():
    await log.ainfo("Starting server")
    server = Server(AuthorizationServicer(), QuotaServicer(), 50051)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
