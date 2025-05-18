from io import BytesIO
from uuid import UUID
from src.api.repos.mysql_repo import mysql_repo

from fastapi import APIRouter, HTTPException, Request, status

from src.api.db.resource import ProjectTemplate, StudentProject
from src.api.deps import AuthorizeDependency, SessionDependency
from src.api.repos.docker_repo import docker_repo
from src.conf import settings, uploadfile_queue

r = APIRouter()


@r.put("/upload")
async def flet_uploads(request: Request, name: str, auth: AuthorizeDependency, session: SessionDependency, template_id: UUID, queue_token: str):
    # check on file extension and so on
    filesize = 0
    buffer = BytesIO()
    queue = uploadfile_queue[queue_token]
    async for chunk in request.stream():
        filesize += len(chunk)
        buffer.write(chunk)

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
    service_name = f'{student.account.login}_{name}'
    if await docker_repo.is_service_name_exists(service_name):
        raise HTTPException(
            status_code=422, detail='Project exists')
    domain_name = f'{student.account.login}.{name}'
    image = await docker_repo.build_student_project(queue, template.dockerfile, buffer, tag=domain_name)

    await docker_repo.create_serverless_service(service_name, student.group.middleware_name.split('@')[0], middleware=student.group.middleware_name, image=image, domain=domain_name)
    queue.put_nowait('Сервис создан')
    student.logical_used += filesize
    project_url = f'http://{domain_name}.{settings.domain}'
    student_project = StudentProject(project_template_id=template_id,
                                     name=name, byte_size=filesize, project_url=project_url)
    student_project.student = student
    session.add(student)
    session.add(student_project)
    await session.commit()
    await mysql_repo.on_create_project(student_project)
    uploadfile_queue.pop(queue_token)
    raise HTTPException(
        status_code=status.HTTP_418_IM_A_TEAPOT, detail={
            'url': project_url}
    )
