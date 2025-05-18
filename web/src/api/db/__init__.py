from sqlmodel import SQLModel  # noqa: F401

from .resource import MySQLDataBase, ResourceTemplate, StudentProject  # noqa: F401
from .users import Account, Group, Student  # noqa: F401
