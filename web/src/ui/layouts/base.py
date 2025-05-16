import flet as ft
from flet_easy import Datasy


class BaseLayout:
    def __init__(self, datasy: Datasy):
        self._datasy = datasy

    async def build(self, control: ft.Control):
        return ft.View(
            controls=[ft.Container(
                control
            )],
            padding=0,
            bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLUE_600),
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER


        )
