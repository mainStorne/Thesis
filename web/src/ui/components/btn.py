import flet as ft


class ThesisButton(ft.Button):
    def __init__(self, text: str, bgcolor=ft.Colors.WHITE, text_color=ft.Colors.BLACK, expand=False, **kwargs):
        super().__init__(**kwargs,
                         bgcolor=bgcolor, content=ft.Text(
                             text, color=text_color),
                         expand=expand,
                         style=ft.ButtonStyle(
                             padding=ft.padding.symmetric(20, 40), side=ft.BorderSide(1, ft.Colors.BLACK)),

                         )
