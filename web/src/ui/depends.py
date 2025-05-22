from src.api.repos.users_repo import users_repo
from src.conf import database


def user(func):
    async def wrapped(data, *args, **kwargs):
        token = await data.page.client_storage.get_async("token")
        async with database.session_maker() as session:
            user = await users_repo.get_user_by_token(session, token)

        return await func(data, **kwargs, user=user)

    return wrapped
