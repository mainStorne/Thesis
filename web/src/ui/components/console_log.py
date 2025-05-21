from secrets import token_urlsafe

import flet as ft

from src.conf import uploadfile_queue

from .btn import ThesisButton
from .log_panel import ThesisListPanel


class ConsoleLogComponent:

    def __init__(self, data):
        self.data = data
        self.list_panel = ThesisListPanel(width=500, )
        self.console_log = ft.AlertDialog(
            title=ft.Text("Сборка проекта"),
            content=self.list_panel,
            alignment=ft.alignment.center,
            title_padding=ft.padding.all(25),
            scrollable=True,
        )
        self.queue_token = token_urlsafe(4)
        self.log_btn = ft.Ref[ft.Button]()
        self.queue = uploadfile_queue[self.queue_token]

    async def on_message(self):

        result = await self.queue.get()
        self.log_btn.current.visible = True
        self.data.page.open(self.console_log)
        while True:
            result = await self.queue.get()
            self.list_panel.add_message(result)

    def build(self):
        return ThesisButton(
            "Посмотреть логи сборки",
            on_click=lambda _: self.data.page.open(
                self.console_log),
            visible=False,
            ref=self.log_btn,
        )
