from fastapi import Depends
from sqlalchemy import select, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Solution
from app.database.database import session_generator
from app.schemas.solution import SolutionFilter

class SolutionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, user_id: int, task_id: int) -> Solution | None:
        return await self.db.scalar(
            select(Solution).where(
                Solution.user_id == user_id,
                Solution.task_id == task_id,
            )
        )

    async def get_by_id(self, solution_id: int) -> Solution | None:
        result = await self.db.execute(
            select(Solution)
            .options(selectinload(Solution.user))
            .where(Solution.id == solution_id)
        )
        return result.scalars().first()

    async def get_by_task_id_with_filters(self, task_id: int, filters: SolutionFilter) -> list[Solution]:
        query = (
            select(Solution)
            .options(selectinload(Solution.user))
            .where(Solution.task_id == task_id)
        )
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
            query = query.order_by(asc(column) if filters.sort_order == "asc" else desc(column))

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, solution: Solution) -> Solution:
        self.db.add(solution)
        return solution

    async def save(self, solution: Solution) -> Solution:
        self.db.add(solution)
        return solution

    async def get_with_attempts(self, solution_id: int) -> Solution | None:
        return await self.db.scalar(
            select(Solution)
            .options(selectinload(Solution.attempts))
            .where(Solution.id == solution_id)
        )

def get_solution_repository(db: AsyncSession = Depends(session_generator)):
    return SolutionRepository(db)
