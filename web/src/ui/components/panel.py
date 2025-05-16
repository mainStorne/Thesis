import flet as ft


class ThesisPanel(ft.Container):
    def __init__(self, width=400, height=300, border_radius=15, padding=15, **kwargs):
        super().__init__(**kwargs,
                         bgcolor=ft.Colors.with_opacity(
                             0.95, ft.Colors.WHITE54),
                         width=width, height=height,
                         border_radius=border_radius,
                         padding=padding)
