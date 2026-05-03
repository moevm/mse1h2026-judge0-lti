from fastapi import Depends
from sqlalchemy import select, func, and_, asc, desc
from sqlalchemy.orm import Session, selectinload

from app.database.database import session_generator
from app.database.models import Module, ModuleTaskOrder, Task, TaskTest, Solution, Attempt
from app.schemas.analytics import UserModulesFilter, UserTasksFilter, AttemptsFilter


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_modules(
        self, user_id: int, filters: UserModulesFilter
    ) -> list[Module]:
        query = (
            select(Module)
            .join(ModuleTaskOrder, ModuleTaskOrder.module_id == Module.id)
            .join(Task, Task.id == ModuleTaskOrder.task_id)
            .join(Solution, Solution.task_id == Task.id)
            .where(Solution.user_id == user_id)
            .distinct()
        )

        if filters.search:
            query = query.where(Module.title.ilike(f"%{filters.search}%"))

        col = {
            "name": Module.title,
            "created_at": Module.created_at,
        }.get(filters.sort_by, Module.created_at)

        query = query.order_by(desc(col) if filters.sort_order == "desc" else asc(col))

        return self.db.scalars(query).all()

    def get_user_tasks_in_module(
        self, user_id: int, module_id: int, filters: UserTasksFilter
    ):
        attempt_count_subq = (
            select(
                Attempt.solution_id,
                func.count().label("attempt_count"),
            )
            .group_by(Attempt.solution_id)
            .subquery()
        )

        last_attempt_subq = (
            select(
                Attempt.solution_id,
                func.max(Attempt.created_at).label("last_attempt"),
            )
            .group_by(Attempt.solution_id)
            .subquery()
        )

        query = (
            select(
                Task,
                Solution,
                func.coalesce(attempt_count_subq.c.attempt_count, 0),
                last_attempt_subq.c.last_attempt,
                func.count(TaskTest.id).label("test_count"),
            )
            .join(ModuleTaskOrder, ModuleTaskOrder.task_id == Task.id)
            .join(
                Solution,
                and_(
                    Solution.task_id == Task.id,
                    Solution.user_id == user_id,
                ),
            )
            .outerjoin(TaskTest, TaskTest.task_id == Task.id)
            .outerjoin(
                attempt_count_subq, attempt_count_subq.c.solution_id == Solution.id
            )
            .outerjoin(
                last_attempt_subq, last_attempt_subq.c.solution_id == Solution.id
            )
            .where(ModuleTaskOrder.module_id == module_id)
            .group_by(
                Task.id,
                Solution.id,
                attempt_count_subq.c.attempt_count,
                last_attempt_subq.c.last_attempt,
            )
        )

        if filters.search:
            query = query.where(Task.title.ilike(f"%{filters.search}%"))

        if filters.status == "passed":
            query = query.where(Solution.is_solved.is_(True))
        elif filters.status == "failed":
            query = query.where(Solution.is_solved.is_(False))

        if filters.attempt_count_min is not None:
            query = query.having(
                func.coalesce(attempt_count_subq.c.attempt_count, 0)
                >= filters.attempt_count_min
            )

        if filters.last_attempt_from:
            query = query.where(
                last_attempt_subq.c.last_attempt >= filters.last_attempt_from
            )

        if filters.last_attempt_to:
            query = query.where(
                last_attempt_subq.c.last_attempt <= filters.last_attempt_to
            )

        if filters.test_count_min is not None:
            query = query.having(func.count(TaskTest.id) >= filters.test_count_min)

        col = {
            "title": Task.title,
            "attempt_count": attempt_count_subq.c.attempt_count,
            "last_attempt_at": last_attempt_subq.c.last_attempt,
            "test_count": func.count(TaskTest.id),
        }.get(filters.sort_by, Task.title)

        query = query.order_by(desc(col) if filters.sort_order == "desc" else asc(col))

        return self.db.execute(query).all()

    def get_attempt_counts(self, user_id: int, task_ids: list[int]) -> dict[int, int]:
        query = (
            select(
                Solution.task_id,
                func.count(Attempt.id).label("cnt"),
            )
            .join(Attempt, Attempt.solution_id == Solution.id)
            .where(
                Solution.user_id == user_id,
                Solution.task_id.in_(task_ids),
            )
            .group_by(Solution.task_id)
        )

        return {row.task_id: row.cnt for row in self.db.execute(query)}

    def get_last_attempts(self, user_id: int, task_ids: list[int]) -> dict:
        query = (
            select(
                Solution.task_id,
                func.max(Attempt.created_at).label("last"),
            )
            .join(Attempt, Attempt.solution_id == Solution.id)
            .where(
                Solution.user_id == user_id,
                Solution.task_id.in_(task_ids),
            )
            .group_by(Solution.task_id)
        )

        return {row.task_id: row.last for row in self.db.execute(query)}

    def get_task_attempts(
        self, task_id: int, user_id: int, filters: AttemptsFilter
    ) -> list[Attempt]:
        query = (
            select(Attempt)
            .join(Solution, Solution.id == Attempt.solution_id)
            .where(
                Solution.task_id == task_id,
                Solution.user_id == user_id,
            )
        )
        if filters.status == "passed":
            query = query.where(Attempt.is_solved.is_(True))
        elif filters.status == "failed":
            query = query.where(Attempt.is_solved.is_(False))

        if filters.language:
            query = query.where(Attempt.language.ilike(f"%{filters.language}%"))
        if filters.memory_min is not None:
            query = query.where(Attempt.memory_mb >= filters.memory_min)
        if filters.memory_max is not None:
            query = query.where(Attempt.memory_mb <= filters.memory_max)
        if filters.time_min is not None:
            query = query.where(Attempt.time_ms >= filters.time_min)
        if filters.time_max is not None:
            query = query.where(Attempt.time_ms <= filters.time_max)
        if filters.from_date:
            query = query.where(Attempt.created_at >= filters.from_date)
        if filters.to_date:
            query = query.where(Attempt.created_at <= filters.to_date)

        return self.db.scalars(query.order_by(Attempt.created_at.desc())).all()
    def get_attempt_by_id(self, attempt_id: int) -> Attempt | None:
        return self.db.get(Attempt, attempt_id)

    def get_teacher_modules(self, teacher_id: int) -> list[Module]:
        query = select(Module)
        return self.db.scalars(query).all()

    def get_module_tasks(self, module_id: int) -> list[Task]:
        query = select(Task).join(ModuleTaskOrder).where(
            ModuleTaskOrder.module_id == module_id
        )
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
