from src.database import Database
from src.settings import Settings

settings = Settings()
database = Database(settings=settings.database)
