import flet as ft
import flet_easy as fs
from structlog import get_logger

from src.api.db.users import Account, Teacher
from src.api.repos.users_repo import users_repo
from src.conf import database
from src.ui.components.btn import ThesisButton
from src.ui.components.field import ThesisTextField
from src.ui.components.panel import ThesisPanel
from src.ui.components.toast_component import ErrorToast, SuccessToast
from src.ui.layouts.layout import ThesisLayout

log = get_logger()
r = fs.AddPagesy(route_prefix="/teachers")


@r.page(route="/create", protected_route=True)
async def create_user(data: fs.Datasy):
    login = ft.Ref()
    first_name = ft.Ref[ft.TextField]()
    middle_name = ft.Ref[ft.TextField]()
    last_name = ft.Ref[ft.TextField]()

    password = ft.Ref()
    second_password = ft.Ref()

    async def handle_submit(e):
        if password.current.value != second_password.current.value:
            password.current.error_text = 'Пароли не совпадают'
            return
        password.current.error_text = ''
        account = Account(login=login.current.value,
                          hashed_password=password.current.value)
        teacher = Teacher(
            first_name=first_name.current.value,
            middle_name=middle_name.current.value,
            last_name=last_name.current.value,
            account=account,
        )
        async with database.session_maker() as session:
            try:
                await users_repo.create_user(teacher.account)
                session.add(teacher)
                await session.commit()
            except Exception as e:
                await log.awarning('Error in create user', exc_info=e)
                data.page.open(ErrorToast('Ошибка повторите позже'))

            else:
                data.page.open(SuccessToast('Преподаватель создан!'))

    return await ThesisLayout(data).build(
        ThesisPanel(
            content=ft.Column([
                ThesisTextField(label_text="Фамилия", ref=first_name),
                ThesisTextField(label_text="Имя", ref=middle_name),
                ThesisTextField(label_text="Отчество", ref=last_name),
                ThesisTextField(label_text="Логин", ref=login),
                ThesisTextField(label_text="Пароль", ref=password,
                                password=True, can_reveal_password=True,),
                ThesisTextField(label_text="Повторите пароль",
                                ref=second_password, password=True, can_reveal_password=True,),
                ft.Container(ThesisButton(
                    text="Создать", on_click=handle_submit), alignment=ft.alignment.center_right),
            ]),
            height=500,
            width=350,
        )
    )
