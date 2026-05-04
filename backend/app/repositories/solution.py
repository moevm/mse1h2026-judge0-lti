from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.models import Solution
from app.database.database import session_generator


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

    def create(self, solution: Solution) -> Solution:
        self.db.add(solution)
        self.db.flush()
        return solution

    def save(self, solution: Solution) -> None:
        self.db.add(solution)

    def get_with_attempts(self, solution_id: int) -> Solution | None:
        return self.db.scalar(
            select(Solution)
            .options(selectinload(Solution.attempts))
            .where(Solution.id == solution_id)
        )

def get_solution_repository(db: Session = Depends(session_generator)):
    return SolutionRepository(db)