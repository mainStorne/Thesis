from asyncio.queues import Queue
from collections import defaultdict
from contextvars import ContextVar

from src.database import Database
from structlog import get_logger
from src.settings import app_settings


log = get_logger()
database = Database(settings=app_settings.database)
uploadfile_queue = defaultdict(Queue)
queue_var = ContextVar('queue_var')
