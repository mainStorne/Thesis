import flet as ft
import flet_easy as fs

from grpc.aio import AioRpcError
from src import grpc_pool
from src.api.db.users import Account, Student
from src.conf import database
from src.grpc.quota_pb2 import AccountRequest, CreateUserRequest
from src.grpc.quota_pb2_grpc import AuthorizationStub
from src.ui.components.btn import ThesisButton
from src.ui.components.field import ThesisTextField
from src.ui.components.panel import ThesisPanel
from src.ui.layouts.base import BaseLayout
from src.api.services.users_service import users_service
# from src.api.u

r = fs.AddPagesy(route_prefix="/admin-panel")


@r.page(route="", title="Админ панель", protected_route=True)
async def create_user(data: fs.Datasy):
    login = fs.Ref()
    fio = fs.Ref()
    password = fs.Ref()
    group_id = fs.Ref()
    resource_limit = fs.Ref()

    def _parse_fio():
        return fio.c.value.split()

    async def handle_submit(e):
        first_name, middle_name, last_name = _parse_fio()
        account = Account(login=login.c.value, password=password.c.value)
        student = Student(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            logical_limit=resource_limit or "200M",
            group_id=group_id.c.value,
            account=account,
        )
        async with database.session_maker() as session:
            try:
                await users_service.create_student(session, student)
            except Exception:
                login.c.error_text = "Пользователь с таким паролем или логином не найден!"
                data.page.update()
            else:
                login.c.error_text = ""

    return await BaseLayout(data).build(
        ThesisPanel(
            content=ft.Column([
                ThesisTextField(label_text="Фио", ref=fio),
                ThesisTextField(label_text="Группа", ref=group_id),
                ThesisTextField(label_text="Квота", ref=resource_limit),
                ThesisTextField(label_text="Логин", ref=login),
                ThesisTextField(label_text="Пароль"),
                ft.Container(ThesisButton(
                    text="Создать", on_click=handle_submit), alignment=ft.alignment.center_right),
            ]),
            height=500,
            width=350,
        )
    )
