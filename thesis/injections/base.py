from functools import wraps
from typing import Union


class Inject:
    def __init__(self, sub_injection: Union["Inject", None] = None):
        self._sub_injection = sub_injection
        if self._sub_injection:
            self._wrap = self._sub_injection__call__
        else:
            self._wrap = self._origin__call__

    def _origin__call__(self, func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            return await self.__inject__(func, *args, **kwargs)

        return wrapped

    def __call__(self, func):
        return self._wrap(func)

    def _set_state(self, dict_: dict):
        pass

    def _sub_injection__call__(self, func):
        @self._sub_injection
        @wraps(func)
        async def wrapped(*args, **kwargs):
            return await self.__inject__(func, *args, **kwargs)

        return wrapped

    def _get_injections(self):
        pass

    async def __inject__(self, func, *args, **kwargs):
        return await func(*args, **kwargs)
