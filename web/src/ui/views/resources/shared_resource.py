import flet as ft
import flet_easy as fs

from src.api.repos.mysql_repo import mysql_repo
from src.conf import database
from src.ui.components.btn import ThesisButton
from src.ui.components.field import ThesisTextField
from src.ui.components.panel import ThesisPanel
from src.ui.layouts.base import BaseLayout

r = fs.AddPagesy(route_prefix='/resources/shared')


@r.page(route="/create/mysql")
async def mysql_create(data: fs.Datasy):
    mysql_name = ft.Ref[ft.TextField]()
    limit = ft.Ref[ft.TextField]()
    btn = ft.Ref[ft.Button]()

    def on_change(e):
        if not mysql_name.current.value:
            btn.current.disabled = True
        else:
            btn.current.disabled = False
        data.page.update()

    async def handle_submit(e):
        async with database.session_maker() as session:
            try:
                if await mysql_repo.is_exists(session, mysql_repo.current.name):
                    mysql_name.c.error_text = "База данных с таким именем уже существует"
                    data.page.update()
                    return
                await mysql_repo.create(session, mysql_name.current.name)
                data.page.go('/shared')

            except Exception:
                mysql_name.c.error_text = "Что-то пошло не так повторите позже"
                data.page.update()
                return

    return await BaseLayout(data).build(
        ThesisPanel(
            content=ft.Column(
                [
                    ft.Column(
                        [
                            ThesisTextField(
                                "Имя базы данных", ref=mysql_name, on_change=on_change),
                            ThesisTextField(
                                "Лимит на хранение данных", ref=limit, on_change=on_change),
                        ],
                        spacing=20,
                    ),
                    ft.Container(
                        ThesisButton(on_click=handle_submit, text="Создать", ref=btn, disabled=True), alignment=ft.alignment.center_right
                    ),
                ],
                spacing=10,
            ),
        )
    )


@r.page(route="")
async def shared_resources(data: fs.Datasy):
    async with database.session_maker() as session:
        shared = await mysql_repo.list(session)

    return await BaseLayout(data).build(
        ThesisPanel(
            content=ft.Column(
                [
                    ft.Column(
                        [
                        ],
                        spacing=20,
                    ),
                    ft.Container(
                        ThesisButton(on_click=lambda _: data.page.go('/shared/id'), text="Создать"), alignment=ft.alignment.center_right
                    ),
                ],
                spacing=10,
            ),
        )
    )
