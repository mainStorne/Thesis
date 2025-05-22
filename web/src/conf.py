from asyncio.queues import Queue
from collections import defaultdict
from contextvars import ContextVar

from src.database import Database
from structlog import get_logger
from src.settings import AppSettings


log = get_logger()
app_settings = AppSettings()
database = Database(settings=app_settings.database)
uploadfile_queue = defaultdict(Queue)
queue_var = ContextVar('queue_var')
