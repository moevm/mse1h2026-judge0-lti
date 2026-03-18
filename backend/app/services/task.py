from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.database.models import Task
from app.database.database import session_generator


class TaskNotFoundException(Exception):
    pass


class TaskService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_task_by_id(self, task_id: int) -> Task:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise TaskNotFoundException
        return task


def get_task_service(db: Session = Depends(session_generator)) -> TaskService:
    return TaskService(db=db)
