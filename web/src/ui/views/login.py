import flet as ft
import flet_easy as fs

from grpc.aio import AioRpcError
from src.grpc.quota_pb2 import AccountRequest
from src.grpc_connection import grpc_connection
from src.ui.components.btn import ThesisButton
from src.ui.components.field import ThesisTextField
from src.ui.components.panel import ThesisPanel
from src.ui.layouts.base import BaseLayout

r = fs.AddPagesy()


@r.page(route="/login", title="Вход")
async def login(data: fs.Datasy):
    login = fs.Ref()
    password = fs.Ref()

    async def handle_submit(e):
        stub = grpc_connection.auth_stub
        try:
            request = await stub.LoginUser(AccountRequest(login=login.c.value, password=password.c.value))
        except AioRpcError:
            login.c.error_text = 'Пользователь с таким паролем или логином не найден!'
            data.page.update()
            return
        else:
            login.c.error_text = ''
            await data.login_async(
                key='token', value=request.token, next_route='/console'
            )

    return await BaseLayout(data).build(
        ThesisPanel(content=ft.Column([
            ft.Column([ThesisTextField('Логин', ref=login),
                       ThesisTextField('Пароль', password=True,
                                       can_reveal_password=True, ref=password),

                       ], spacing=20),
            ft.Container(ThesisButton(on_click=handle_submit,
                                      text='Вход'),
                         alignment=ft.alignment.center_right)
        ],
            spacing=10,


        ),
        )
    )
