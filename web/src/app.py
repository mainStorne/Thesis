import flet as ft
import flet_easy as fs

from src.ui.views import admin_panel, console, login
from src.ui.views.resources import shared_resource


class App:

    def __init__(self):
        self._app = fs.FletEasy(route_init='/console', route_login='/login')
        self._app.add_pages(
            [login.r, admin_panel.r, console.r, shared_resource.r])
        self._app.login(self.handle_login)
        self._app.config(self.on_config)

    def on_config(self, page: ft.Page):
        theme = ft.Theme()
        platforms = ["android", "ios", "macos", "linux", "windows"]
        for platform in platforms:  # Removing animation on route change.
            setattr(theme.page_transitions, platform,
                    ft.PageTransitionTheme.NONE)

        theme.text_theme = ft.TextTheme()
        page.theme = theme
        page.padding = 0
        page.margin = 0

    async def handle_login(self, data: fs.Datasy):
        return bool(await data.page.client_storage.get_async('token'))
