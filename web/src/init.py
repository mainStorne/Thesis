
from structlog import get_logger

from src.api.services.resource_service import MysqlExists, resource_service
from src.conf import database
from src.grpc_pool import grpc_pool

log = get_logger()


async def on_init():
    async with database.session_maker() as session:
        try:
            await resource_service.create_mysql(session, name='mysql', limit='5G', grpc_pool=grpc_pool)
        except MysqlExists:
            await log.ainfo('Mysql was created')
        except Exception as e:
            await log.awarning('Mysql Exception', exc_info=e)
        else:
            await log.ainfo('Mysql created')
