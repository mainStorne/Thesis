from contextlib import asynccontextmanager
from src.conf import database
from src.injections.base import scoped


@asynccontextmanager
async def get_session(state: dict):
    async with database._session_maker() as session:
        state['session'] = session
        yield session

session_scoped = scoped([get_session])
