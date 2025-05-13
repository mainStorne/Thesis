from src.database import Database
from src.settings import EnvSettings

settings = EnvSettings()
database = Database(settings=settings.database)
