import flet as ft


class ThesisTextField(ft.TextField):
    def __init__(self, label_text: str, **kwargs):
        super().__init__(label=ft.Text(label_text, color=ft.Colors.BLACK),  color=ft.Colors.BLACK,
                         error_style=ft.TextStyle(
            weight=ft.FontWeight.BOLD, color=ft.Colors.RED_ACCENT), **kwargs)
