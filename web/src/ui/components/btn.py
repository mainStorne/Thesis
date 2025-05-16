import flet as ft


class ThesisButton(ft.Button):
    def __init__(self, text: str, **kwargs):
        super().__init__(**kwargs,
                         bgcolor=ft.Colors.WHITE, content=ft.Text(
                             text, color=ft.Colors.BLACK),
                         style=ft.ButtonStyle(
                             padding=ft.padding.symmetric(20, 40), side=ft.BorderSide(1, ft.Colors.BLACK)),

                         )
