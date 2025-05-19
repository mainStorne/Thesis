
from typing import Any, Callable

import flet as ft


class ThesisDropdown(ft.Dropdown):

    def __init__(self, icon: ft.Icons, label_text: str, on_dropdown_change: Callable[[ft.ControlEvent], Any], options: list[ft.DropdownOption], **kwargs):

        super().__init__(leading_icon=ft.Icon(icon, color=ft.Colors.BLACK), label=label_text, label_style=ft.TextStyle(color=ft.Colors.BLACK), text_style=ft.TextStyle(
            color=ft.Colors.BLACK), on_change=on_dropdown_change,  options=options,
            expand=True, **kwargs
        ),
