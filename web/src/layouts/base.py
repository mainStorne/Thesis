import flet as ft
from flet_easy import Datasy


class BaseLayout:
    def __init__(self, datasy: Datasy):
        self._datasy = datasy

    async def build(self, control: ft.Control):
        return ft.View(
            controls=[ft.Container(
                control, bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.GREEN_400), expand=True
            )],
            padding=0,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER


        )
