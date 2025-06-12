from uuid import UUID

from sqlalchemy.orm import joinedload
from sqlmodel import select

from src.api.db.resource import Project, ProjectImage
from src.api.repos.base import BaseSQLRepo


class ProjectImageService(BaseSQLRepo):
    __root__ = ProjectImage

    async def delete_project(self, project_name: str):
        pass

    async def get_by_id(self, session, id: UUID) -> Project | None:
        return (await session.exec(select(Project).where(Project.id == str(id)).options(joinedload(Project.project_image)))).one_or_none()


project_image_service = ProjectImageService()
