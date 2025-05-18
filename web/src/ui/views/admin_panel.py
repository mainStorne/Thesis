import flet as ft
import flet_easy as fs
from structlog import get_logger

from src.api.db.users import Account, Student
from src.api.repos.mysql_repo import mysql_repo
from src.api.repos.users_repo import users_repo
from src.conf import database
from src.ui.components.btn import ThesisButton
from src.ui.components.field import ThesisTextField
from src.ui.components.panel import ThesisPanel
from src.ui.layouts.base import CenteredLayout

log = get_logger()
r = fs.AddPagesy(route_prefix="/admin-panel")


@r.page(route="", title="Админ панель", protected_route=True)
async def create_user(data: fs.Datasy):
    login = ft.Ref()
    first_name = ft.Ref[ft.TextField]()
    middle_name = ft.Ref[ft.TextField]()
    last_name = ft.Ref[ft.TextField]()

    password = ft.Ref()
    group_id = ft.Ref()
    resource_limit = ft.Ref()

    async def handle_submit(e):
        account = Account(login=login.current.value,
                          hashed_password=password.current.value)
        student = Student(
            first_name=first_name.current.value,
            middle_name=middle_name.current.value,
            last_name=last_name.current.value,
            logical_limit=resource_limit.current.value if resource_limit.current.value else 200_000_00,
            group_id=group_id.current.value,
            account=account,
        )
        async with database.session_maker() as session:
            try:
                await users_repo.create_student(session, student)
                await mysql_repo.on_student_create(student, password.current.value)
            except Exception as e:
                await log.awarning('Error in create student', exc_info=e)
                login.current.error_text = "Ошибка повторите позже"
                data.page.update()
            else:
                login.current.error_text = ""

    return await CenteredLayout(data).build(
        ThesisPanel(
            content=ft.Column([
                ThesisTextField(label_text="Фамилия", ref=first_name),
                ThesisTextField(label_text="Имя", ref=middle_name),
                ThesisTextField(label_text="Отчество", ref=last_name),
                ThesisTextField(label_text="Группа", ref=group_id),
                ThesisTextField(label_text="Квота", ref=resource_limit),
                ThesisTextField(label_text="Логин", ref=login),
                ThesisTextField(label_text="Пароль", ref=password),
                ft.Container(ThesisButton(
                    text="Создать", on_click=handle_submit), alignment=ft.alignment.center_right),
            ]),
            height=500,
            width=350,
        )
    )
