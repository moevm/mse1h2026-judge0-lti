from typing import List

from fastapi import Depends
from sqlalchemy import select, or_
from sqlalchemy.orm import Session, selectinload

from app.database.models import Task, Language
from app.database.database import session_generator
from app.schemas.task import TaskFilter
from sqlalchemy import asc, desc


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Task]:
        query = select(Task).options(selectinload(Task.languages))
        return self.db.scalars(query).all()

    def get_by_id(self, task_id: int) -> Task | None:
        query = (
            select(Task).options(selectinload(Task.languages), selectinload(Task.tests)).where(Task.id == task_id)
        )
        return self.db.scalars(query).first()

    def add(self, task: Task):
        self.db.add(task)

    def delete(self, task: Task):
        self.db.delete(task)

    def get_filtered(self, filters: TaskFilter):
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
            if filters.sort_order == "asc":
                query = query.order_by(asc(column))
            else:
                query = query.order_by(desc(column))
        return self.db.scalars(query).all()

    def save(self, task: Task):
        self.db.flush()
        self.db.refresh(task)
        return task


def get_task_repository(db: Session = Depends(session_generator)) -> TaskRepository:
    return TaskRepository(db)
