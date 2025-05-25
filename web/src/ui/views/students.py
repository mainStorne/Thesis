import flet as ft
import flet_easy as fs
from sqlmodel import select
from structlog import get_logger

from src.api.db.users import Account, Group, Student
from src.api.repos.users_repo import users_repo
from src.conf import database
from src.ui.components.btn import ThesisButton
from src.ui.components.dropdown import ThesisDropdown
from src.ui.components.field import ThesisText, ThesisTextField
from src.ui.components.panel import ThesisPanel
from src.ui.components.toast_component import ErrorToast, SuccessToast
from src.ui.layouts.layout import ThesisLayout
from src.ui.utils import from_string_to_bytes

log = get_logger()
r = fs.AddPagesy(route_prefix="/students")


@r.page(route="/create", protected_route=True)
async def create_student(data: fs.Datasy):
    async with database.session_maker() as session:
        groups = (await session.exec(select(Group))).all()

    if not groups:
        # handle this
        pass
    login = ft.Ref()
    first_name = ft.Ref[ft.TextField]()
    middle_name = ft.Ref[ft.TextField]()
    last_name = ft.Ref[ft.TextField]()

    password = ft.Ref()
    second_password = ft.Ref()
    group_id = None
    resource_limit = ft.Ref()

    def on_dropdown_change(e: ft.ControlEvent):
        nonlocal group_id
        group_id = e.control.value

    options = [
        ft.DropdownOption(key=group.id,
                          text=group.name,
                          style=ft.ButtonStyle(
                              bgcolor=ft.Colors.WHITE,
                              padding=0,
                              shape=ft.ContinuousRectangleBorder()
                          ),
                          text_style=ft.TextStyle(
                              color=ft.Colors.BLACK),
                          content=ThesisText(value=group.name, text_align=ft.TextAlign.CENTER)) for group in groups]

    async def handle_submit(e):
        if password.current.value != second_password.current.value:
            password.current.error_text = 'Пароли не совпадают'
            return
        if not group_id:
            return
        logical_limit = from_string_to_bytes(resource_limit.current.value)
        password.current.error_text = ''
        account = Account(login=login.current.value,
                          hashed_password=password.current.value)
        account = Account(login=login.current.value,
                          hashed_password=password.current.value)
        student = Student(
            first_name=first_name.current.value,
            middle_name=middle_name.current.value,
            last_name=last_name.current.value,
            group_id=group_id,
            logical_limit=logical_limit,
            account=account,
        )
        async with database.session_maker() as session:
            try:
                await users_repo.create_user(student.account)
                session.add(student)
                await session.commit()
            except Exception as e:
                await log.awarning('Error in create user', exc_info=e)
                data.page.open(ErrorToast('Ошибка повторите позже'))

            else:
                data.page.open(SuccessToast('Студент создан!'))

    return await ThesisLayout(data).build(
        ThesisPanel(
            content=ft.Column([
                ThesisTextField(label_text="Фамилия", ref=first_name),
                ThesisTextField(label_text="Имя", ref=middle_name),
                ThesisTextField(label_text="Отчество", ref=last_name),
                ThesisTextField(label_text="Квота", ref=resource_limit),
                ThesisDropdown(
                    ft.Icons.DASHBOARD_CUSTOMIZE, 'Группы',
                    on_dropdown_change=on_dropdown_change, options=options),
                ThesisTextField(label_text="Логин", ref=login),
                ThesisTextField(label_text="Пароль", ref=password,
                                password=True, can_reveal_password=True,),
                ThesisTextField(label_text="Повторите пароль",
                                ref=second_password, password=True, can_reveal_password=True,),
                ft.Container(ThesisButton(
                    text="Создать", on_click=handle_submit), alignment=ft.alignment.center_right),
            ]),
            height=600,
            width=350,
        )
    )
