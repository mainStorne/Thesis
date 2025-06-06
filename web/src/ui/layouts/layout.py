import flet as ft

from src.api.db.users import Account
from src.api.repos.mysql_repo import mysql_repo
from src.api.repos.users_repo import users_repo
from src.conf import database, log
from src.ui.components.field import ThesisText
from src.ui.components.toast_component import ErrorToast, SuccessToast
from src.ui.layouts.base import BaseLayout


class ThesisLayout(BaseLayout):
    def on_nav_rail_change(self, e):
        index = int(e.control.selected_index)
        if index == 0:
            self.data.page.go("/users/me/projects/create")
        elif index == 1:
            self.data.page.go("/users/me/projects")
        elif index == 2:
            self.data.page.go("/images")
        elif index == 3:
            self.data.page.go("/images/create")
        elif index == 4:
            self.data.page.go("/teachers/create")
        elif index == 5:
            self.data.page.go("/groups/create")
        elif index == 6:
            self.data.page.go("/students/create")

    def _create_mysql(self, account: Account):
        async def wrapped(e):
            try:
                await mysql_repo.create_database(account)
            except Exception as e:
                await log.aexception("exc", exc_info=e)
                self.data.page.open(ErrorToast("Ошибка попробуйте позже!"))
            else:
                self.data.page.open(SuccessToast("База данных была создана!"))

        return wrapped

    async def build(self, control):
        token = await self.data.page.client_storage.get_async("token")
        async with database.session_maker() as session:
            user = await users_repo.get_user_by_token(session, token)

        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            bgcolor=ft.Colors.WHITE60,
            min_extended_width=400,
            leading=ft.FloatingActionButton(icon=ft.Icons.CREATE, text="Mysql", on_click=self._create_mysql(user)),
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.BOOKMARK)
                    if self.data.page.route == "/users/me/projects/create"
                    else ft.Icons.BOOK,
                    label_content=ThesisText(value="Создать Проект"),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.LIST) if self.data.page.route == "/users/me/projects" else ft.Icons.LIST,
                    label_content=ThesisText(value="Проекты"),
                ),
            ],
            on_change=self.on_nav_rail_change,
        )

        if user.teacher:
            fio = user.teacher.fio
            text = "Учитель"

        elif user.student:
            fio = user.student.fio
            text = "Студент"
        else:
            text = "Администратор"
            fio = ""

        if user.teacher or user.is_stuff:
            rail.destinations.append(
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.INBOX_SHARP) if self.data.page.route == "/images" else ft.Icons.INBOX_SHARP,
                    label_content=ThesisText(value="Образы"),
                ),
            )
            rail.destinations.append(
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.ADD_BOX) if self.data.page.route == "/images/create" else ft.Icons.ADD_BOX,
                    label_content=ThesisText(value="Создать Образ"),
                ),
            )

            rail.destinations.append(
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.ADD_TASK)
                    if self.data.page.route == "/teachers/create"
                    else ft.Icons.ADD_TASK,
                    label_content=ThesisText(value="Создать преподавателя"),
                ),
            )

            rail.destinations.append(
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.ADD_TASK) if self.data.page.route == "/groups/create" else ft.Icons.ADD_TASK,
                    label_content=ThesisText(value="Создать группу"),
                ),
            )

            rail.destinations.append(
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.ADD_TASK)
                    if self.data.page.route == "/students/create"
                    else ft.Icons.ADD_TASK,
                    label_content=ThesisText(value="Создать студента"),
                ),
            )

        return await super().build(
            ft.Column(
                [
                    ft.Container(
                        ft.Row(
                            [
                                ft.Text(value="Thesis", color=ft.Colors.WHITE),
                                ft.Row(
                                    [
                                        ft.Text(text, color=ft.Colors.WHITE),
                                        ft.Text(value=fio, color=ft.Colors.WHITE),
                                        ft.IconButton(
                                            icon=ft.Icons.EXIT_TO_APP,
                                            icon_color=ft.Colors.RED,
                                            on_click=self.data.logout("token"),
                                        ),
                                    ],
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.padding.only(left=30, right=10),
                        bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLUE_900),
                        expand=1,
                    ),
                    ft.Container(
                        ft.Row(
                            [
                                ft.Container(
                                    rail, expand=1, border=ft.border.only(top=ft.BorderSide(1, ft.Colors.BLUE_600))
                                ),
                                ft.Container(control, alignment=ft.alignment.center, expand=9),
                            ],
                            expand=True,
                        ),
                        expand=15,
                    ),
                ],
                expand=True,
                spacing=0,
            ),
            expand=True,
        )
