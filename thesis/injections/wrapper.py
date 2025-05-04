from functools import wraps

from grpc import StatusCode
from grpc.aio import ServicerContext
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from thesis.db.users import Account
from thesis.injections.session_injection import session_injection
from thesis.services.security_service import DecodeException, ISecurityService


def auth(security: ISecurityService, token_header: str):
    def inject(func, user_type: type[SQLModel]):
        @session_injection
        @wraps(wrapped=func)
        async def wrapped(*args, **kwargs):
            context: ServicerContext = kwargs["context"]
            session: AsyncSession = kwargs["session"]
            if token := dict(context.invocation_metadata).get(token_header):
                try:
                    payload = security.decode(token)
                except DecodeException:
                    await context.abort(StatusCode.UNAUTHENTICATED, details="Token is wrong")

                account = await session.get(Account, payload.id)
                if not account:
                    await context.abort(StatusCode.UNAUTHENTICATED, details="Token is wrong")

                return await func(*args, **kwargs, token=token, payload=payload, profile=account)
            else:
                await context.abort(StatusCode.UNAUTHENTICATED, details="Token is missing")

        return wrapped

    return inject
