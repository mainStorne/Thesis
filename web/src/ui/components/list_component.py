import flet as ft


class ListComponent(ft.ListView):
    def __init__(self, **kwargs):
        super().__init__(auto_scroll=True, expand=True, spacing=5)

    def _handle_hover(self, container: ft.Container, recover=ft.Colors.AMBER, hover=ft.Colors.AMBER_600):
        def wrapped(e: ft.HoverEvent):
            if e.data == 'true':
                container.bgcolor = hover
            else:
                container.bgcolor = recover
            self.page.update()

        return wrapped

    def append(self, content, **kwargs) -> None:
        container = ft.Container(border_radius=ft.border_radius.all(5),
                                 padding=13,
                                 content=content, bgcolor=ft.Colors.AMBER, **kwargs)
        container.on_hover = self._handle_hover(container)
        self.controls.append(container)
