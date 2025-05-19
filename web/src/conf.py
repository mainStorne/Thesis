from asyncio.queues import Queue
from collections import defaultdict

from src.database import Database
from src.settings import AppSettings

app_settings = AppSettings()
database = Database(settings=app_settings.database)
uploadfile_queue = defaultdict(Queue)
