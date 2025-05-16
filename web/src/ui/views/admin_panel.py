import flet as ft
import flet_easy as fs

from grpc.aio import AioRpcError
from src import grpc_connection
from src.grpc.quota_pb2 import AccountRequest, CreateUserRequest
from src.grpc.quota_pb2_grpc import AuthorizationStub
from src.ui.components.btn import ThesisButton
from src.ui.components.field import ThesisTextField
from src.ui.components.panel import ThesisPanel
from src.ui.layouts.base import BaseLayout

r = fs.AddPagesy(route_prefix='/admin-panel')


@r.page(route="", title="Админ панель", protected_route=True)
async def create_user(data: fs.Datasy):
    login = fs.Ref()
    fio = fs.Ref()
    password = fs.Ref()
    password2 = fs.Ref()
    group_id = fs.Ref()
    resource_limit = fs.Ref()

    def _parse_fio():
        return fio.c.value.split()

    async def handle_submit(e):
        stub = AuthorizationStub(grpc_connection.channel)
        first_name, middle_name, last_name = _parse_fio()
        try:
            request = await stub.CreateUser(CreateUserRequest(student=CreateUserRequest.Student(profile=CreateUserRequest.Profile(
                first_name=first_name, middle_name=middle_name, last_name=last_name,
                account=AccountRequest(
                    login=login.c.value, password=password.c.value)
            ), group_id=group_id.c.value, resource_limit=resource_limit.c.value)))
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
        ThesisPanel(
            content=ft.Column([
                ThesisTextField(label_text='Фио', ref=fio),
                ThesisTextField(label_text='Группа', ref=group_id),
                ThesisTextField(label_text='Квота', ref=resource_limit),
                ThesisTextField(label_text='Логин', ref=login),
                ThesisTextField(label_text='Пароль'
                                ),
                ft.Container(ThesisButton(
                    text='Создать', on_click=handle_submit), alignment=ft.alignment.center_right)
            ]),
            height=500,
            width=350
        )
    )
