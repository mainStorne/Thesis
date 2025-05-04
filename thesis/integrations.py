from thesis.database import Database
from thesis.settings import Settings

settings = Settings()
database = Database(settings=settings.database)
