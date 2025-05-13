from contextlib import asynccontextmanager

from sqlmodel.ext.asyncio.session import AsyncSession

from grpc import StatusCode
from grpc.aio import ServicerContext
from src.db.users import Account
from src.repos.security_repo import DecodeException, TokenIsMissing, security_repo, token_validator_repo


@asynccontextmanager
async def authorize(state: dict):
    context: ServicerContext = state["context"]
    session: AsyncSession = state["session"]
    metadata = dict(context.invocation_metadata())
    try:
        token = token_validator_repo.validate(metadata)
    except TokenIsMissing:
        await context.abort(StatusCode.UNAUTHENTICATED, details="Token is missing")
    try:
        payload = security_repo.decode(token)
    except DecodeException:
        await context.abort(StatusCode.UNAUTHENTICATED, details="Token is wrong")

    account = await session.get(Account, payload.id)
    if not account:
        await context.abort(StatusCode.UNAUTHENTICATED, details="Token is wrong")

    state["metadata"] = metadata
    state['account'] = account
    yield
