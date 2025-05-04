from contextlib import asynccontextmanager

from thesis.integrations import settings
from thesis.repositories.auth_repository import AuthRepository
from thesis.services.account_service import AcountService
from thesis.services.quota_service import QuotaService
from thesis.services.security_service import JwtSecurityService


@asynccontextmanager
async def auth_repository(state: dict):
    session = state.get("get_session")
    yield AuthRepository(
        QuotaService(session=session), AcountService(session), JwtSecurityService(settings.jwt_secret, "HS256")
    )
