from typing import Optional
from fastapi import Depends
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from app.database.database import session_generator
from app.database.models import (
    Module, ModuleTaskOrder, Task, TaskTest,
    Solution, Attempt
)


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_modules(self, user_id: int) -> list:
        # модули где у пользователя есть хотя бы одна попытка
        query = (
            select(Module)
            .join(ModuleTaskOrder, ModuleTaskOrder.module_id == Module.id)
            .join(Task, Task.id == ModuleTaskOrder.task_id)
            .join(Solution, and_(
                Solution.task_id == Task.id,
                Solution.user_id == user_id
            ))
            .distinct()
        )
        return self.db.scalars(query).all()

    def get_module_task_count(self, module_id: int) -> int:
        query = select(func.count()).select_from(ModuleTaskOrder).where(
            ModuleTaskOrder.module_id == module_id
        )
        return self.db.scalar(query)

    def get_user_tasks_in_module(self, user_id: int, module_id: int) -> list:
        query = (
            select(Task, Solution)
            .join(ModuleTaskOrder, ModuleTaskOrder.task_id == Task.id)
            .join(Solution, and_(
                Solution.task_id == Task.id,
                Solution.user_id == user_id
            ))
            .where(ModuleTaskOrder.module_id == module_id)
        )
        return self.db.execute(query).all()

    def get_attempt_count(self, user_id: int, task_id: int) -> int:
        query = select(func.count()).select_from(Attempt).where(
            and_(
                Attempt.solution_user_id == user_id,
                Attempt.solution_task_id == task_id
            )
        )
        return self.db.scalar(query)

    def get_last_attempt_at(self, user_id: int, task_id: int):
        query = (
            select(func.max(Attempt.created_at))
            .where(and_(
                Attempt.solution_user_id == user_id,
                Attempt.solution_task_id == task_id
            ))
        )
        return self.db.scalar(query)

    def get_task_test_count(self, task_id: int) -> int:
        query = select(func.count()).select_from(TaskTest).where(
            TaskTest.task_id == task_id
        )
        return self.db.scalar(query)

    def get_task_attempts(self, task_id: int, user_id: int) -> list[Attempt]:
        query = select(Attempt).where(
            and_(
                Attempt.solution_task_id == task_id,
                Attempt.solution_user_id == user_id
            )
        ).order_by(Attempt.created_at.desc())
        return self.db.scalars(query).all()

    def get_attempt_by_id(self, attempt_id: int) -> Attempt | None:
        return self.db.get(Attempt, attempt_id)

    def get_teacher_modules(self, teacher_id: int) -> list:
        query = select(Module).where(Module.teacher_id == teacher_id)
        return self.db.scalars(query).all()

    def get_module_tasks(self, module_id: int) -> list:
        query = select(Task).join(ModuleTaskOrder).where(ModuleTaskOrder.module_id == module_id)
        return self.db.scalars(query).all()

    def has_solution(self, user_id: int, task_id: int) -> bool:
        query = select(Solution).where(
            Solution.user_id == user_id,
            Solution.task_id == task_id
        )
        return self.db.scalar(query) is not None


def get_analytics_repository(
    db: Session = Depends(session_generator)
) -> AnalyticsRepository:
    return AnalyticsRepository(db)
