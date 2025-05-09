import flet as ft
import flet_easy as fs
from flet_easy.route import FletEasyX
from grpc.aio import insecure_channel

from src.state import State
from src.views import login


class App(fs.FletEasy):

    def __init__(self, route_prefix=None, route_login=None, on_resize=False, on_Keyboard=False, secret_key=None, auto_logout=False, path_views=None):
        super().__init__(route_prefix, '/home', route_login, on_resize,
                         on_Keyboard, secret_key, auto_logout, path_views)
        self.add_pages([login.r])

    def on_config(self, page: ft.Page):
        pass

    async def __call__(self, page):
        channel = await insecure_channel('localhost:50051').__aenter__()
        page.state = State(channel)
        flet_easy_x = FletEasyX(
            page=page,
            route_prefix=self._FletEasy__route_prefix,
            route_init=self._FletEasy__route_init,
            route_login=self._FletEasy__route_login,
            config_login=self._FletEasy__config_login,
            pages=self._FletEasy__pages,
            page_404=self._FletEasy__page_404,
            view_data=self._FletEasy__view_data,
            view_config=self._FletEasy__view_config,
            config_event_handler=None,
            on_resize=self._FletEasy__on_resize,
            on_Keyboard=self._FletEasy__on_Keyboard,
            secret_key=self._FletEasy__secret_key,
            auto_logout=self._FletEasy__auto_logout,
            middleware=self._FletEasy__middlewares,
        )
        return flet_easy_x.run()
