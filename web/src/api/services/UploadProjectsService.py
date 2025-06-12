

from io import BytesIO
from zipfile import BadZipFile

from aiodocker import DockerError
from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.db.resource import Project
from src.api.db.users import Account
from src.api.services.base import NotFound
from src.api.services.project_service import project_service
from src.conf import log, queue_var, uploadfile_queue
from src.schemas import DomainLikeName


async def create_project(session: AsyncSession, buffer: BytesIO, filesize: int, account: Account, project_name: str, queue_token: str):

    if filesize == 0:
        raise HTTPException(
            status_code=422, detail='File with no size')

    try:
        project_name = DomainLikeName(project_name)
    except ValidationError:
        raise HTTPException(  # noqa: B904
            status_code=422, detail='Project name is wrong'
        )

    queue = uploadfile_queue[queue_token]
    queue_var.set(queue)

    try:
        project = await project_service.create_project(project_name, account, buffer, session, filesize)
    except NotFound as e:
        await queue.put("Ошибка!")
        raise HTTPException(status_code=404, detail=str(e)) from e
    except BadZipFile as e:
        await queue.put("Ошибка!")
        raise HTTPException(
            status_code=422, detail='Zipfile errro') from e
    except Exception as e:
        await log.aexception('Exception creaing project', exc_info=e)
        await queue.put("Ошибка!")
        raise
    except DockerError as e:
        await log.aexception('Exception creaing project', exc_info=e)
        await queue.put("Ошибка в докеробразе!")
        raise
    finally:
        uploadfile_queue.pop(queue_token)

    raise HTTPException(
        status_code=status.HTTP_418_IM_A_TEAPOT, detail={
            'id': str(project.id), 'url': project.project_url}
    )


async def update_project(session, project: Project, filesize: int, buffer, queue_token, account,):

    if filesize == 0:
        raise HTTPException(
            status_code=422, detail='File with no size')

    queue = uploadfile_queue[queue_token]
    queue_var.set(queue)
    try:
        await project_service.update_project(project, account, buffer)
        project.byte_size = filesize
        session.add(project)
        await session.commit()
    except BadZipFile as e:
        raise HTTPException(
            status_code=422, detail='Zipfile error') from e
    except Exception as e:
        await log.aexception('Exception creaing project', exc_info=e)
        raise
    finally:
        uploadfile_queue.pop(queue_token)

    raise HTTPException(
        status_code=status.HTTP_418_IM_A_TEAPOT, detail={
            'id': str(project.id), 'url': project.project_url}
    )
