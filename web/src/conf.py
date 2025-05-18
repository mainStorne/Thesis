from src.database import Database
from src.settings import AppSettings

settings = AppSettings()
database = Database(settings=settings.database)
