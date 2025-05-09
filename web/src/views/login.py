import flet as ft
import flet_easy as fs

from src.layouts.base import BaseLayout
from src.schemas.generated.quota_pb2 import AccountRequest
from src.schemas.generated.quota_pb2_grpc import AuthorizationStub

r = fs.AddPagesy()


# We add a page
@r.page(route="/home", title="Home")
async def index_page(data: fs.Datasy):
    stub = AuthorizationStub(data.page.state.grpc_channel)
    request = await stub.LoginUser(AccountRequest(login='dima3', password='dima3'))
    return await BaseLayout(data).build(
        [
            ft.Text("Home page", size=30),
            ft.FilledButton("Go to Counter",
                            on_click=data.go("/counter/test/0")),
        ]
    )
