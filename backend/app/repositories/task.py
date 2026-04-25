from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Task
from app.database.database import session_generator


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id) -> Task | None:
        return self.db.get(Task, task_id)


def get_task_repository(db: Session = Depends(session_generator)) -> TaskRepository:
    return TaskRepository(db)