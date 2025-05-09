from contextlib import asynccontextmanager

from src.integrations import settings
from src.repositories.auth_repository import AuthRepository
from src.services.account_service import AcountService
from src.services.quota_service import QuotaService
from src.services.security_service import JwtSecurityService


@asynccontextmanager
async def auth_repository(state: dict):
    session = state.get("get_session")
    yield AuthRepository(
        QuotaService(session=session), AcountService(session), JwtSecurityService(settings.jwt_secret, "HS256")
    )
