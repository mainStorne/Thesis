import flet as ft
from flet_easy import Datasy


class BaseLayout:
    def __init__(self, data: Datasy):
        self.data = data

    async def build(self, control: ft.Control, expand=False, **kwargs, ):
        return ft.View(
            controls=[ft.Container(
                control,
                expand=expand,
            )],
            padding=0,
            bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLUE_600),
            **kwargs

        )


class CenteredLayout(BaseLayout):
    def __init__(self, datasy: Datasy):
        self._datasy = datasy

    async def build(self, control: ft.Control):
        return await super().build(
            control,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
