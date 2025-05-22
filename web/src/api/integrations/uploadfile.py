from io import BytesIO
from uuid import UUID
from zipfile import BadZipFile

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import ValidationError
from structlog import get_logger

from src.api.deps import AuthorizeDependency, AuthStudentDependency, SessionDependency
from src.api.services.base import NotFound
from src.api.services.project_service import project_service
from src.conf import queue_var, uploadfile_queue
from src.schemas import DomainLikeName

log = get_logger()
r = APIRouter()


@r.put("/student/upload")
async def create_project(request: Request, project_name: str, auth: AuthStudentDependency, session: SessionDependency, template_id: UUID, queue_token: str):
    filesize = 0
    buffer = BytesIO()
    async for chunk in request.stream():
        filesize += len(chunk)
        buffer.write(chunk)

    buffer.seek(0)
    student, _ = auth
    if student.logical_limit < student.logical_used + filesize:
        raise HTTPException(
            status_code=422, detail='Limit is full')

    try:
        project_name = DomainLikeName(project_name)
    except ValidationError:
        raise HTTPException(  # noqa: B904
            status_code=422, detail='Project name is wrong'
        )
    if filesize == 0:
        raise HTTPException(
            status_code=422, detail='File with no size')

    queue = uploadfile_queue[queue_token]
    queue_var.set(queue)
    try:
        student_project = await project_service.create_project(project_name, student.account, buffer, session, template_id, filesize)
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except BadZipFile as e:
        raise HTTPException(
            status_code=422, detail='Zipfile errro') from e
    except Exception as e:
        await log.aexception('Exception creaing project', exc_info=e)
        raise
    finally:
        uploadfile_queue.pop(queue_token)

    raise HTTPException(
        status_code=status.HTTP_418_IM_A_TEAPOT, detail={
            'id': str(student_project.id), 'url': student_project.project_url}
    )


@r.put("/teacher/upload")
async def create_techer_project(request: Request, project_name: str, auth: AuthorizeDependency, session: SessionDependency, template_id: UUID, queue_token: str):
    filesize = 0
    buffer = BytesIO()
    async for chunk in request.stream():
        filesize += len(chunk)
        buffer.write(chunk)

    buffer.seek(0)
    account, _ = auth

    try:
        project_name = DomainLikeName(project_name)
    except ValidationError:
        raise HTTPException(  # noqa: B904
            status_code=422, detail='Project name is wrong'
        )
    if filesize == 0:
        raise HTTPException(
            status_code=422, detail='File with no size')

    queue = uploadfile_queue[queue_token]
    queue_var.set(queue)
    try:
        project = await project_service.create_project(project_name, account, buffer, session, template_id, filesize)
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except BadZipFile as e:
        raise HTTPException(
            status_code=422, detail='Zipfile errro') from e
    except Exception as e:
        await log.aexception('Exception creaing project', exc_info=e)
        raise
    finally:
        uploadfile_queue.pop(queue_token)

    raise HTTPException(
        status_code=status.HTTP_418_IM_A_TEAPOT, detail={
            'id': str(project.id), 'url': project.project_url}
    )
