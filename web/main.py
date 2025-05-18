
import flet.fastapi as flet_fastapi

from src.api.integrations import uploadfile
from src.app import App
from src.grpc_pool import grpc_pool
from src.init import on_init

app = flet_fastapi.FastAPI(on_startup=[grpc_pool.on_startup, on_init], on_shutdown=[

                           grpc_pool.on_shutdown])

app.include_router(
    uploadfile.r
)

app.mount("/", flet_fastapi.app(App()._app.get_app()))
