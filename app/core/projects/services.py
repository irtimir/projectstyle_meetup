from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import Page, Paginator
from app.core.projects.exceptions import ProjectNotFoundError
from app.core.projects.models import Project


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_list(
        self,
        offset: int = 0,
        limit: int = 20,
        owner_id: int | None = None,
    ) -> Page[Project]:
        query = select(Project).order_by(Project.id)

        if owner_id is not None:
            query = query.where(Project.owner_id == owner_id)

        return await Paginator(self.session, query).get_page(offset, limit)

    async def get_by_id(self, project_id: int) -> Project:
        project = await self.session.get(Project, project_id)
        if not project:
            raise ProjectNotFoundError()
        return project

    async def create(
        self,
        name: str,
        owner_id: int,
        description: str | None = None,
    ) -> Project:
        project = Project(name=name, owner_id=owner_id, description=description)
        self.session.add(project)
        await self.session.flush()
        return project

    async def update(
        self,
        project_id: int,
        name: str | None = None,
        description: str | None = None,
    ) -> Project:
        project = await self.get_by_id(project_id)
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        await self.session.flush()
        return project

    async def delete(self, project_id: int) -> None:
        project = await self.get_by_id(project_id)
        await self.session.delete(project)
        await self.session.flush()
