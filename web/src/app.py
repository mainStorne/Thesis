import flet as ft
import flet_easy as fs

from src.ui.views import admin_panel, login
from src.ui.views.users import projects


class App:

    def __init__(self):
        self._app = fs.FletEasy(
            route_init=projects.r.route_prefix, route_login='/login')
        self._app.add_pages(
            [login.r, admin_panel.r, projects.r])
        self._app.login(self.handle_login)
        self._app.config(self.on_config)
        # self._app.page_404(route='/not-found',
        #                    title='Не найдено')(self.not_found)

    # def not_found(self, data: fs.Datasy):
    #     return ft.View(
    #         route="/not-found",  controls=[
    #             ft.Text('Не найдено')
    #         ])

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
