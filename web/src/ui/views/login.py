import flet as ft
import flet_easy as fs

from src.api.services.auth_service import UserNotFoundException, auth_service
from src.conf import database
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
        async with database.session_maker() as session:
            try:
                token = await auth_service.login(session, login.c.value, password.c.value)
            except UserNotFoundException:
                login.c.error_text = "Пользователь с таким паролем или логином не найден!"
                data.page.update()
                return
            except Exception as e:
                login.c.error_text = "Что-то пошло не так повторите позже"
                data.page.update()
                return

            else:
                login.c.error_text = ""
                await data.login_async(key="token", value=token, next_route="/console")

    return await BaseLayout(data).build(
        ThesisPanel(
            content=ft.Column(
                [
                    ft.Column(
                        [
                            ThesisTextField("Логин", ref=login),
                            ThesisTextField(
                                "Пароль", password=True, can_reveal_password=True, ref=password),
                        ],
                        spacing=20,
                    ),
                    ft.Container(
                        ThesisButton(on_click=handle_submit, text="Вход"), alignment=ft.alignment.center_right
                    ),
                ],
                spacing=10,
            ),
        )
    )
