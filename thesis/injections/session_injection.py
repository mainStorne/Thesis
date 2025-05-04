from thesis.injections.base import scoped
from thesis.integrations import database

session_scoped = scoped([database.get_session])
