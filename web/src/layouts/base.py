import flet as ft
from flet_easy import Datasy


class BaseLayout:
    def __init__(self, datasy: Datasy):
        self._datasy = datasy

    async def build(self, controls: list[ft.Control]):
        return ft.View(
            controls=controls
        )
