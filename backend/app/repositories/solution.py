from typing import List
from fastapi import Depends
from sqlalchemy import select, asc, desc
from sqlalchemy.orm import Session, selectinload

from app.database.models import Solution
from app.database.database import session_generator
from app.schemas.solution import SolutionFilter


class SolutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: int, task_id: int) -> Solution | None:
        return self.db.scalar(
            select(Solution).where(
                Solution.user_id == user_id,
                Solution.task_id == task_id,
            )
        )

    def get_by_id(self, solution_id: int) -> Solution | None:
        query = select(Solution).options(selectinload(Solution.user)).where(Solution.id == solution_id)
        return self.db.scalars(query).first()

    def get_by_task_id_with_filters(self, task_id: int, filters: SolutionFilter) -> List[Solution]:
        query = select(Solution).options(selectinload(Solution.user)).where(Solution.task_id == task_id)

        if filters.is_solved is not None:
            query = query.where(Solution.is_solved == filters.is_solved)

        if filters.score_min is not None:
            query = query.where(Solution.score >= filters.score_min)

        if filters.score_max is not None:
            query = query.where(Solution.score <= filters.score_max)

        if filters.updated_from is not None:
            query = query.where(Solution.updated_at >= filters.updated_from)

        if filters.updated_to is not None:
            query = query.where(Solution.updated_at <= filters.updated_to)

        if filters.sort_by:
            column = getattr(Solution, filters.sort_by)
            if filters.sort_order == "asc":
                query = query.order_by(asc(column))
            else:
                query = query.order_by(desc(column))

        return self.db.scalars(query).all()

    def create(self, solution: Solution) -> Solution:
        self.db.add(solution)
        self.db.flush()
        return solution

    def save(self, solution: Solution) -> Solution:
        self.db.add(solution)
        self.db.flush()
        self.db.refresh(solution)
        return solution

    def get_with_attempts(self, solution_id: int) -> Solution | None:
        return self.db.scalar(
            select(Solution)
            .options(selectinload(Solution.attempts))
            .where(Solution.id == solution_id)
        )


def get_solution_repository(db: Session = Depends(session_generator)):
    return SolutionRepository(db)
