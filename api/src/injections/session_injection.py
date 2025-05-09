from src.injections.base import scoped
from src.integrations import database

session_scoped = scoped([database.get_session])
