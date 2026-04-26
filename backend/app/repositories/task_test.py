from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import session_generator
from app.database.models import TaskTest

class TaskTestRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_task_id(self, task_id: int):
        query = select(TaskTest).where(TaskTest.task_id == task_id)
        return self.db.scalars(query).all()

    def get_by_id(self, test_id: int):
        query = select(TaskTest).where(TaskTest.id == test_id)
        return self.db.scalars(query).first()

    def add(self, test: TaskTest):
        self.db.add(test)

    def add_all(self, tests: list[TaskTest]):
        self.db.add_all(tests)

    def delete(self, test: TaskTest):
        self.db.delete(test)

    def save(self, test: TaskTest):
        self.db.flush()
        self.db.refresh(test)

    def flush(self):
        self.db.flush()


def get_task_test_repository(db: Session = Depends(session_generator)) -> TaskTestRepository:
    return TaskTestRepository(db)
