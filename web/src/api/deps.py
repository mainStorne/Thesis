from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import contains_eager
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.db.users import Account, Student
from src.api.repos.security_repo import DecodeException, Payload, security_repo
from src.conf import database


async def get_session():
    async with database.session_maker() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session)]


async def authorize(token: str, session: SessionDependency):
    try:
        payload = security_repo.decode(token)
    except DecodeException:
        raise HTTPException(status_code=422, detail="Token is wrong")  # noqa: B904

    stmt = select(Account).where(Account.id == payload.id)
    account = (await session.exec(stmt)).one_or_none()
    if not account:
        raise HTTPException(status_code=422, detail="Token is wrong")

    return account, payload


async def auhorize_student(token: str, session: SessionDependency):
    try:
        payload = security_repo.decode(token)
    except DecodeException:
        raise HTTPException(status_code=422, detail="Token is wrong")  # noqa: B904

    stmt = select(Student).join(Account, Account.id ==
                                Student.account_id).where(Account.id == payload.id).options(contains_eager(Student.account))
    student = (await session.exec(stmt)).one_or_none()
    if not student:
        raise HTTPException(status_code=422, detail="Token is wrong")

    return student, payload


AuthorizeDependency = Annotated[tuple[Account, Payload], Depends(authorize)]
AuthStudentDependency = Annotated[tuple[Student,
                                        Payload], Depends(auhorize_student)]
