from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from structlog import get_logger

from src.api.db.resource import Project
from src.api.deps import AuthorizeDependency, AuthStudentDependency, SessionDependency
from src.api.services import UploadProjectsService

log = get_logger()
r = APIRouter()


@r.post("/student/upload")
async def create_project(request: Request, project_name: str, auth: AuthStudentDependency, session: SessionDependency, queue_token: str):
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
    await UploadProjectsService.create_project(session, buffer,  filesize, student.account, project_name, queue_token)


@r.post("/teacher/upload")
async def create_techer_project(request: Request, project_name: str, auth: AuthorizeDependency, session: SessionDependency, queue_token: str):
    filesize = 0
    buffer = BytesIO()
    async for chunk in request.stream():
        filesize += len(chunk)
        buffer.write(chunk)

    buffer.seek(0)
    account, _ = auth
    await UploadProjectsService.create_project(session, buffer, filesize, account, project_name, queue_token)


@r.put("/student/upload")
async def update_project(request: Request, project_id: UUID,  auth: AuthStudentDependency, session: SessionDependency, queue_token: str):

    student, _ = auth
    project = await session.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=404, detail='Project not found')

    filesize = 0
    buffer = BytesIO()
    async for chunk in request.stream():
        filesize += len(chunk)
        buffer.write(chunk)

    buffer.seek(0)

    if student.logical_limit < (student.logical_used + filesize - project.byte_size):
        raise HTTPException(
            status_code=422, detail='Limit is full')

    await UploadProjectsService.update_project(session, project, filesize, buffer, queue_token, student.account)


@r.put("/teacher/upload")
async def update_techer_project(request: Request, project_id: UUID,  auth: AuthorizeDependency, session: SessionDependency, queue_token: str):
    project = await session.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=404, detail='Project not found')

    filesize = 0
    buffer = BytesIO()
    async for chunk in request.stream():
        filesize += len(chunk)
        buffer.write(chunk)

    buffer.seek(0)
    account, _ = auth

    await UploadProjectsService.update_project(session, project, filesize, buffer, queue_token, account)
