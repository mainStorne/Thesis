import asyncio

from structlog import get_logger

from src.api.db.users import Account
from src.api.repos.mysql_repo import mysql_repo
from src.api.services.resource_service import MysqlExists, NoAgentAvailable, resource_service
from src.conf import app_settings, database
from src.grpc_pool import grpc_pool

log = get_logger()


async def on_init():
    async with database.session_maker() as session:
        try:
            await resource_service.create_mysql(
                session, name="mysql", root_password=app_settings.mysql.password, limit="5G", grpc_pool=grpc_pool
            )
            # Wait for one minute
            await asyncio.sleep(60)
            await mysql_repo.create_user_account(Account(login='admin'), app_settings.admin.password)
        except MysqlExists:
            await log.ainfo("Mysql was created")
        except NoAgentAvailable:
            await log.awarning("No agent available, skipping mysql bootstrap")
        except Exception as e:
            await log.awarning("Mysql Exception", exc_info=e)
        else:
            await log.ainfo("Mysql created")
