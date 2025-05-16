from httpcore import AnyIOBackend
from src.api.repos.security_repo import DecodeException, Payload, security_repo
from src.api.db.users import Account
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from typing import Annotated, Tuple

from fastapi import Depends
from src.conf import database


async def get_session():
    async with database._session_maker() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session)]


async def authorize(token: str, session: SessionDependency):
    try:
        payload = security_repo.decode(token)
    except DecodeException:
        raise HTTPException(status_code=422, detail="Token is wrong")  # noqa: B904

    account = await session.get(Account, payload.id)
    if not account:
        raise HTTPException(status_code=422, detail="Token is wrong")

    return account, payload

AuthorizeDependency = Annotated[tuple[Account, Payload], Depends(authorize)]
