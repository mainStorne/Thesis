from thesis.injections.base import Inject
from thesis.injections.session_injection import session_inject
from thesis.integrations import settings
from thesis.repositories.auth_repository import AuthRepository
from thesis.services.account_service import AcountService
from thesis.services.quota_service import QuotaService
from thesis.services.security_service import JwtSecurityService


class AuthInject(Inject):
    async def __inject__(self, func, *args, **kwargs):
        session = kwargs.pop("session")
        return await super().__inject__(
            func,
            *args,
            **kwargs,
            auth_repository=AuthRepository(
                QuotaService(session=session), AcountService(session), JwtSecurityService(settings.jwt_secret, "HS256")
            ),
        )


auth_inject = AuthInject(session_inject)
