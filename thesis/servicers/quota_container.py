from dependency_injector import containers, providers

from ..database import Database
from ..settings import Settings
from .quota_repository import QuotaRepository
from .quota_service import QuotaService


class QuotaContainer(containers.DeclarativeContainer):
    config = providers.Configuration(pydantic_settings=[Settings()])
    db = providers.Singleton(Database, settings=config.database)
    session = db.provided.get_session
    quota_service = providers.Factory(QuotaService, session=session)
    quota_repository = providers.Factory(QuotaRepository, quota_service=quota_service)
