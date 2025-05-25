import flet as ft
import flet_easy as fs
from structlog import get_logger

from src.api.db.users import Group
from src.conf import database
from src.ui.components.btn import ThesisButton
from src.ui.components.field import ThesisTextField
from src.ui.components.panel import ThesisPanel
from src.ui.components.toast_component import ErrorToast, SuccessToast
from src.ui.layouts.layout import ThesisLayout

log = get_logger()
r = fs.AddPagesy(route_prefix="/groups")


@r.page(route="/create", protected_route=True)
async def create_user(data: fs.Datasy):
    name = ft.Ref()

    async def handle_submit(e):
        if not name.current.value:
            return
        async with database.session_maker() as session:
            try:
                group = Group(name=name.current.value)
                session.add(group)
                await session.commit()
            except Exception as e:
                await log.awarning('Error in create user', exc_info=e)
                data.page.open(ErrorToast('Ошибка повторите позже'))

            else:
                data.page.open(SuccessToast('Группа создана!'))

    return await ThesisLayout(data).build(
        ThesisPanel(
            content=ft.Column([
                ThesisTextField(label_text="Название группы", ref=name),
                ft.Container(ThesisButton(
                    text="Создать", on_click=handle_submit), alignment=ft.alignment.center_right),
            ]),
            height=500,
            width=350,
        )
    )
