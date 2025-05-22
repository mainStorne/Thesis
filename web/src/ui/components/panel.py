import flet as ft


class ThesisPanel(ft.Container):
    def __init__(self, border_radius=15, padding=15, **kwargs):
        super().__init__(content=ft.Container(
            content=ft.Container(**kwargs,
                         bgcolor=ft.Colors.with_opacity(
                             0.95, ft.Colors.WHITE54),
                         border_radius=border_radius,
                         padding=padding),
            expand=True, padding=20, bgcolor=ft.Colors.WHITE, border_radius=ft.border_radius.all(10)), margin=15, expand=True)
