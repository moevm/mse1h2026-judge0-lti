from fastapi import Depends
from sqlalchemy import select, func, and_, asc, desc
from sqlalchemy.orm import Session, selectinload

from app.database.database import session_generator
from app.database.models import Module, ModuleTaskOrder, Task, TaskTest, Solution, Attempt
from app.schemas.analytics import UserModulesFilter, UserTasksFilter, AttemptsFilter


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_modules(self, user_id: int, filters: UserModulesFilter) -> list[Module]:
        query = (
            select(Module)
            .options(selectinload(Module.task_links))
            .join(ModuleTaskOrder, ModuleTaskOrder.module_id == Module.id)
            .join(Task, Task.id == ModuleTaskOrder.task_id)
            .join(Solution, and_(
                Solution.task_id == Task.id,
                Solution.user_id == user_id
            ))
            .distinct()
        )

        if filters.search:
            query = query.where(Module.title.ilike(f"%{filters.search}%"))

        if filters.sort_by == "name":
            col = Module.title
        elif filters.sort_by == "created_at":
            col = Module.created_at
        else:
            col = Module.created_at

        if filters.sort_order == "desc":
            query = query.order_by(desc(col))
        else:
            query = query.order_by(asc(col))

        return self.db.scalars(query).all()

    def get_user_tasks_in_module(
        self, user_id: int, module_id: int, filters: UserTasksFilter
    ) -> list[tuple]:
        # Подзапрос для количества попыток
        attempt_count_subq = (
            select(
                Attempt.solution_task_id,
                func.count().label("attempt_count")
            )
            .where(Attempt.solution_user_id == user_id)
            .group_by(Attempt.solution_task_id)
            .subquery()
        )

        # Подзапрос для последней попытки
        last_attempt_subq = (
            select(
                Attempt.solution_task_id,
                func.max(Attempt.created_at).label("last_attempt")
            )
            .where(Attempt.solution_user_id == user_id)
            .group_by(Attempt.solution_task_id)
            .subquery()
        )

        # Основной запрос
        query = (
            select(
                Task,
                Solution,
                func.coalesce(attempt_count_subq.c.attempt_count, 0).label("attempt_count"),
                last_attempt_subq.c.last_attempt.label("last_attempt_at"),
                func.count(TaskTest.id).label("test_count")
            )
            .join(ModuleTaskOrder, ModuleTaskOrder.task_id == Task.id)
            .join(Solution, and_(
                Solution.task_id == Task.id,
                Solution.user_id == user_id
            ))
            .outerjoin(TaskTest, TaskTest.task_id == Task.id)
            .outerjoin(attempt_count_subq, attempt_count_subq.c.solution_task_id == Task.id)
            .outerjoin(last_attempt_subq, last_attempt_subq.c.solution_task_id == Task.id)
            .where(ModuleTaskOrder.module_id == module_id)
            .group_by(Task.id, Solution.is_solved, attempt_count_subq.c.attempt_count, last_attempt_subq.c.last_attempt)
        )

        # Фильтры
        if filters.search:
            query = query.where(Task.title.ilike(f"%{filters.search}%"))

        if filters.status == "passed":
            query = query.where(Solution.is_solved == True)
        elif filters.status == "failed":
            query = query.where(Solution.is_solved == False)

        if filters.attempt_count_min is not None:
            query = query.where(func.coalesce(attempt_count_subq.c.attempt_count, 0) >= filters.attempt_count_min)

        if filters.last_attempt_from:
            query = query.where(last_attempt_subq.c.last_attempt >= filters.last_attempt_from)

        if filters.last_attempt_to:
            query = query.where(last_attempt_subq.c.last_attempt <= filters.last_attempt_to)

        if filters.test_count_min is not None:
            query = query.where(func.count(TaskTest.id) >= filters.test_count_min)

        # Сортировка
        if filters.sort_by == "title":
            col = Task.title
        elif filters.sort_by == "attempt_count":
            col = attempt_count_subq.c.attempt_count
        elif filters.sort_by == "last_attempt_at":
            col = last_attempt_subq.c.last_attempt
        elif filters.sort_by == "test_count":
            col = func.count(TaskTest.id)
        else:
            col = Task.title

        if filters.sort_order == "desc":
            query = query.order_by(desc(col))
        else:
            query = query.order_by(asc(col))

        return self.db.execute(query).all()

    def get_attempt_counts(self, user_id: int, task_ids: list[int]) -> dict[int, int]:
        query = (
            select(Attempt.solution_task_id, func.count().label("cnt"))
            .where(and_(
                Attempt.solution_user_id == user_id,
                Attempt.solution_task_id.in_(task_ids)
            ))
            .group_by(Attempt.solution_task_id)
        )
        return {row.solution_task_id: row.cnt for row in self.db.execute(query)}

    def get_last_attempts(self, user_id: int, task_ids: list[int]) -> dict:
        query = (
            select(Attempt.solution_task_id, func.max(Attempt.created_at).label("last"))
            .where(and_(
                Attempt.solution_user_id == user_id,
                Attempt.solution_task_id.in_(task_ids)
            ))
            .group_by(Attempt.solution_task_id)
        )
        return {row.solution_task_id: row.last for row in self.db.execute(query)}

    def get_task_attempts(
        self, task_id: int, user_id: int, filters: AttemptsFilter
    ) -> list[Attempt]:
        query = select(Attempt).where(
            and_(
                Attempt.solution_task_id == task_id,
                Attempt.solution_user_id == user_id
            )
        )

        if filters.status == "passed":
            query = query.where(Attempt.is_solved == True)
        elif filters.status == "failed":
            query = query.where(Attempt.is_solved == False)

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

        query = query.order_by(Attempt.created_at.desc())
        return self.db.scalars(query).all()

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
