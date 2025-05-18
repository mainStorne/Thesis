from collections import defaultdict
from src.database import Database
from src.settings import AppSettings
from asyncio.queues import Queue
from contextvars import ContextVar

settings = AppSettings()
database = Database(settings=settings.database)
uploadfile_queue = defaultdict(Queue)
