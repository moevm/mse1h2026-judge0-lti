from typing import List

from fastapi import Depends
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Task, Language
from app.database.database import session_generator
from app.schemas.task import TaskFilter
from sqlalchemy import asc, desc

class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Task]:
        result = await self.db.execute(
            select(Task).options(selectinload(Task.languages))
        )
        return result.scalars().all()

    async def get_by_id(self, task_id: int) -> Task | None:
        result = await self.db.execute(
            select(Task)
            .options(selectinload(Task.languages), selectinload(Task.tests), selectinload(Task.module_links),)
            .where(Task.id == task_id)
        )
        return result.scalars().first()

    async def add(self, task: Task) -> None:
        self.db.add(task)

    async def delete(self, task: Task) -> None:
        await self.db.delete(task)

    async def get_filtered(self, filters: TaskFilter) -> list[Task]:
        query = select(Task).options(
            selectinload(Task.languages),
            selectinload(Task.tests),
        )
        if filters.search:
            search_value = f"%{filters.search}%"
            query = query.where(
                or_(
                    Task.title.ilike(search_value),
                    Task.description.ilike(search_value),
                    Task.languages.any(Language.language.ilike(search_value)),
                )
            )
        if filters.timeout_from is not None:
            query = query.where(Task.timeout >= filters.timeout_from)
        if filters.timeout_to is not None:
            query = query.where(Task.timeout <= filters.timeout_to)
        if filters.created_from:
            query = query.where(Task.created_at >= filters.created_from)
        if filters.created_to:
            query = query.where(Task.created_at <= filters.created_to)
        if filters.updated_from:
            query = query.where(Task.updated_at >= filters.updated_from)
        if filters.updated_to:
            query = query.where(Task.updated_at <= filters.updated_to)
        if filters.sort_by:
            column = getattr(Task, filters.sort_by)
            query = query.order_by(asc(column) if filters.sort_order == "asc" else desc(column))

        result = await self.db.execute(query)
        return result.scalars().all()

def get_task_repository(db: AsyncSession = Depends(session_generator)) -> TaskRepository:
    return TaskRepository(db)
