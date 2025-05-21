from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import ValidationError
from structlog import get_logger

from src.api.db.resource import ProjectTemplate
from src.api.deps import AuthorizeDependency, SessionDependency
from src.api.repos.docker_repo import docker_repo
from src.api.repos.mysql_repo import mysql_repo
from src.api.services.project_service import project_service
from src.conf import queue_var, uploadfile_queue
from src.schemas import DomainLikeName

log = get_logger()
r = APIRouter()


@r.put("/upload")
async def create_project(request: Request, project_name: str, auth: AuthorizeDependency, session: SessionDependency, template_id: UUID, queue_token: str, create_mysql: bool | None = None):
    # check on file extension and so on
    filesize = 0
    buffer = BytesIO()
    async for chunk in request.stream():
        filesize += len(chunk)
        buffer.write(chunk)

    try:
        project_name = DomainLikeName(project_name)
    except ValidationError:
        raise HTTPException(  # noqa: B904
            status_code=422, detail='Domain name is wrong'
        )

    buffer.seek(0)
    if filesize == 0:
        raise HTTPException(
            status_code=422, detail='File with no size')
    student, _ = auth
    if student.logical_limit < student.logical_used + filesize:
        raise HTTPException(
            status_code=422, detail='Limit is full')

    template = await session.get(ProjectTemplate, template_id)
    if not template:
        raise HTTPException(
            status_code=404, detail='Template not found')

    service_name = f'{student.account.login}_{project_name.root}'
    if await docker_repo.is_service_name_exists(service_name):
        raise HTTPException(
            status_code=422, detail='Project exists')

    queue = uploadfile_queue[queue_token]
    queue_var.set(queue)
    try:
        project_url, student_project = await project_service._create_project(project_name.root, session, service_name, filesize, buffer, student, template)
    except Exception as e:
        await log.aexception('Exception creaing project', exc_info=e)
        await queue.put('Произошла ошибка!')
        raise
    finally:
        uploadfile_queue.pop(queue_token)
    if create_mysql:
        mysql = await mysql_repo.on_create_project(student_project)
        session.add(mysql)
        await session.commit()

        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT, detail={
                'id': str(student_project.id), 'url': project_url, 'mysql_account': {'login': mysql.login, 'password': mysql.password}}
        )

    raise HTTPException(
        status_code=status.HTTP_418_IM_A_TEAPOT, detail={
            'id': str(student_project.id), 'url': project_url}
    )
