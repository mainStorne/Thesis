from logging import DEBUG, basicConfig

import flet as ft

from src.app import App

basicConfig(level=DEBUG)


async def main(page):
    app = App()
    return await app(page)

ft.app(main, view=ft.AppView.WEB_BROWSER,
       port=8080)
