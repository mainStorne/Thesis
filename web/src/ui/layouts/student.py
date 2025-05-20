
import flet as ft

from src.ui.components.field import ThesisText

from .base import BaseLayout


class StudentLayout(BaseLayout):

    def on_nav_rail_change(self, e):
        index = int(e.control.selected_index)
        if index == 0:
            self.data.page.go('/users/me/projects')

        # self.data.page.update()

    async def build(self, control):
        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            bgcolor=ft.Colors.WHITE60,

            min_extended_width=400,
            leading=ft.FloatingActionButton(
                icon=ft.Icons.CREATE, text="Создать", on_click=lambda _: self.data.page.go('/users/me/projects/create')
            ),
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        ft.Icons.BOOKMARK) if self.data.page.route == '/users/me/projects' else ft.Icons.BOOK,
                    label_content=ThesisText(value="Проекты")
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.BOOKMARK_BORDER),
                    selected_icon=ft.Icon(ft.Icons.BOOKMARK),
                    label_content=ThesisText(value="Проекты")
                ),
            ],
            on_change=self.on_nav_rail_change
        )

        return await super().build(ft.Column([
            ft.Container(ft.Row([
                ft.Text(value='Thesis', color=ft.Colors.WHITE), ft.Text(
                    value='Dmitry D.D.', color=ft.Colors.WHITE)  # remove this
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLUE_900),  expand=1),
            ft.Container(ft.Row([ft.Container(rail, expand=1, border=ft.border.only(top=ft.BorderSide(1, ft.Colors.BLUE_600))), ft.Container(control,
                                                                                                                                             alignment=ft.alignment.center, expand=9
                                                                                                                                             )], expand=True), expand=15),

        ], expand=True, spacing=0,),
            expand=True
        )
