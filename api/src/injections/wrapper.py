from contextlib import asynccontextmanager

from grpc import StatusCode
from grpc.aio import ServicerContext
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.users import Account
from src.services.security_service import DecodeException, TokenIsMissing, security, token_validator


@asynccontextmanager
async def authorize(state: dict):
    context: ServicerContext = state["context"]
    session: AsyncSession = state["get_session"]
    metadata = dict(context.invocation_metadata())
    try:
        token = token_validator.validate(metadata)
    except TokenIsMissing:
        await context.abort(StatusCode.UNAUTHENTICATED, details="Token is missing")
    try:
        payload = security.decode(token)
    except DecodeException:
        await context.abort(StatusCode.UNAUTHENTICATED, details="Token is wrong")

    account = await session.get(Account, payload.id)
    if not account:
        await context.abort(StatusCode.UNAUTHENTICATED, details="Token is wrong")

    state["metadata"] = metadata
    yield token, payload, account
