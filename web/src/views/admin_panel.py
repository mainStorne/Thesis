import flet as ft
import flet_easy as fs

from grpc.aio import AioRpcError
from src import grpc_connection
from src.grpc.quota_pb2 import AccountRequest, CreateUserRequest
from src.grpc.quota_pb2_grpc import AuthorizationStub
from src.layouts.base import BaseLayout

r = fs.AddPagesy(route_prefix='/admin-panel')  # check that this only stuff


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
        ft.Column([
            ft.TextField(label='Фио', ref=fio),
            ft.TextField(label='Группа', ref=group_id),
            ft.TextField(label='Квота', ref=resource_limit),
            ft.TextField(label='Логин', ref=login),
            ft.TextField(label='Пароль', password=True,
                         can_reveal_password=True, ref=password),
            ft.TextField(label='Повторите пароль', password=True,
                         can_reveal_password=True, ref=password2),
            ft.Button(text='Вход', on_click=handle_submit)
        ])
    )
