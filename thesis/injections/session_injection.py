from thesis.injections.base import Inject
from thesis.integrations import database


class SessionInject(Inject):
    async def __inject__(self, func, *args, **kwargs):
        async with database.get_session() as session:
            return await super().__inject__(func, *args, **kwargs, session=session)


session_inject = SessionInject()
