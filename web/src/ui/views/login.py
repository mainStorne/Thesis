import flet as ft
import flet_easy as fs
from structlog import get_logger

from src.api.services.auth_service import UserNotFoundException, auth_service
from src.conf import database
from src.ui.components.btn import ThesisButton
from src.ui.components.field import ThesisTextField
from src.ui.components.panel import ThesisPanel
from src.ui.layouts.base import CenteredLayout

log = get_logger()
r = fs.AddPagesy()


@r.page(route="/login", title="Вход")
async def login(data: fs.Datasy):
    login = fs.Ref()
    password = fs.Ref()
    button = fs.Ref()

    def set_loading(loading: bool):
        button.c.disabled = loading
        button.c.content = ft.ProgressRing(
            width=16, height=16, color=ft.Colors.WHITE, stroke_width=2
        ) if loading else ft.Text("Вход", color=ft.Colors.WHITE)

    async def handle_submit(e):
        async with database.session_maker() as session:
            set_loading(True)
            data.page.update()
            try:
                token = await auth_service.login(session, login.c.value, password.c.value)
            except UserNotFoundException:
                login.c.error_text = "Пользователь с таким паролем или логином не найден!"
                set_loading(False)
                data.page.update()
                return
            except Exception as e:
                await log.aexception('Login error', exc_info=e)
                login.c.error_text = "Что-то пошло не так повторите позже"
                set_loading(False)
                data.page.update()
                return
            else:
                login.c.error_text = ""
                await data.login_async(key="token", value=token, next_route="/users/me/projects/create")

    return await CenteredLayout(data).build(
        ThesisPanel(
            content=ft.Column(
                [
                    ft.Text("Вход в систему", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                    ft.Text("Введите свои учетные данные, чтобы продолжить", color=ft.Colors.BLACK54),
                    ft.Column(
                        [
                            ThesisTextField("Логин", ref=login, autofocus=True, on_submit=handle_submit),
                            ThesisTextField(
                                "Пароль", password=True, can_reveal_password=True, ref=password,
                                on_submit=handle_submit,
                            ),
                        ],
                        spacing=20,
                    ),
                    ThesisButton(
                        on_click=handle_submit, text="Вход", ref=button,
                        bgcolor=ft.Colors.BLUE_600, text_color=ft.Colors.WHITE, expand=True,
                    ),
                ],
                spacing=15,
            ),
            width=min(400, (data.page.width or 400) - 40),
        )
    )
