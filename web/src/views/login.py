import flet as ft
import flet_easy as fs

from grpc.aio import AioRpcError
from src.grpc.quota_pb2 import AccountRequest, CreateUserRequest
from src.grpc.quota_pb2_grpc import AuthorizationStub
from src.layouts.base import BaseLayout

r = fs.AddPagesy()


# We add a page
@r.page(route="/login", title="Home")
async def index_page(data: fs.Datasy):
    login = fs.Ref()
    password = fs.Ref()

    async def handle_submit(e):
        stub = AuthorizationStub(data.page.state.grpc_channel)
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
        ft.Column([
            ft.TextField(label='Логин', ref=login),
            ft.TextField(label='Пароль', password=True,
                         can_reveal_password=True, ref=password),
            ft.Button(text='Вход', on_click=handle_submit)
        ])
    )


# We add a page
@r.page(route="/register", title="Register")
async def register(data: fs.Datasy):
    login = fs.Ref()
    password = fs.Ref()
    password2 = fs.Ref()

    async def handle_submit(e):
        if password.c.value != password2.c.value:
            password2.c.error_text = 'Пароли должны быть одинаковы!'
            return
        else:
            password2.c.error_text = ''

        stub = AuthorizationStub(data.page.state.grpc_channel)
        request = await stub.CreateUser(CreateUserRequest())

    return await BaseLayout(data).build(
        [
            ft.Column([
                ft.TextField(label='Логин', ref=login),
                ft.TextField(label='Пароль', password=True,
                             can_reveal_password=True, ref=password),
                ft.TextField(label='Повторите пароль', password=True,
                             can_reveal_password=True, ref=password2),
                ft.Button(text='Зарегистрироваться', on_click=handle_submit)
            ])
        ]
    )
