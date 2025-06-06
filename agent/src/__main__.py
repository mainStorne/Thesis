import asyncio

import structlog

from src.init import initialize
from src.server import Server

log = structlog.get_logger()


async def main():
    await log.ainfo("Initialization")
    await initialize()
    await log.ainfo("Starting server")
    server = Server(50051)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
