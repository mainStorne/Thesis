import flet as ft


class ThesisText(ft.Text):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, color=ft.Colors.BLACK)


class ThesisTextField(ft.TextField):
    def __init__(self, label_text: str, **kwargs):
        super().__init__(label=ThesisText(value=label_text),  color=ft.Colors.BLACK,
                         error_style=ft.TextStyle(
            weight=ft.FontWeight.BOLD, color=ft.Colors.RED_ACCENT), **kwargs)
