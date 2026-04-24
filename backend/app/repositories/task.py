from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.models import Task, Language
from app.database.database import session_generator
from app.schemas.task import TaskPatch


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Task]:
        query = select(Task).options(selectinload(Task.languages))
        return self.db.scalars(query).all()

    def get_by_id(self, task_id: int) -> Task | None:
        query = (
            select(Task).options(selectinload(Task.languages)).where(Task.id == task_id)
        )
        return self.db.scalars(query).first()

    def add(self, task: Task):
        self.db.add(task)

    def delete(self, task: Task):
        self.db.delete(task)

    def save(self, task: Task):
        self.db.flush()
        self.db.refresh(task)
        return task


def get_task_repository(db: Session = Depends(session_generator)) -> TaskRepository:
    return TaskRepository(db)
