from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Attempt, Solution
from app.database.database import session_generator
from typing import List

class AttemptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, attempt: Attempt) -> Attempt:
        self.db.add(attempt)
        return attempt

    async def get_by_solution(self, solution_id: int) -> List[Attempt]:
        result = await self.db.execute(
            select(Attempt)
            .where(Attempt.solution_id == solution_id)
            .order_by(Attempt.created_at.desc())
        )
        return result.scalars().all()

    async def count_by_user_and_task(self, user_id: int, task_id: int) -> int:
        query = (
            select(func.count())
            .select_from(Attempt)
            .join(Solution, Solution.id == Attempt.solution_id)
            .where(
                Solution.user_id == user_id,
                Solution.task_id == task_id,
            )
        )
        return await self.db.scalar(query)

    async def get_by_solution_id(self, solution_id: int) -> List[Attempt]:
        result = await self.db.execute(
            select(Attempt)
            .where(Attempt.solution_id == solution_id)
            .order_by(Attempt.created_at)
        )
        return result.scalars().all()

def get_attempt_repository(db: AsyncSession = Depends(session_generator)):
    return AttemptRepository(db)
