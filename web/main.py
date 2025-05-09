from logging import DEBUG, basicConfig

import flet.fastapi as flet_fastapi

from src.app import App
from src.grpc_connection import grpc_connection
from src.integrations import uploadfile

basicConfig(level=DEBUG)


async def main(page):
    app = App()
    return await app(page)


app = flet_fastapi.FastAPI(on_startup=[grpc_connection.on_startup], on_shutdown=[

                           grpc_connection.on_shutdown])

app.include_router(
    uploadfile.r
)


app.mount("/", flet_fastapi.app(main))
