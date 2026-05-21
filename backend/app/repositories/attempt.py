from fastapi import Depends
from sqlalchemy import func, select

from sqlalchemy.orm import Session

from app.database.models import Attempt, Solution
from app.database.database import session_generator


class AttemptRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, attempt: Attempt) -> Attempt:
        self.db.add(attempt)
        self.db.flush()
        return attempt

    def get_by_solution(self, solution_id: int) -> list[Attempt]:
        return self.db.scalars(
            select(Attempt)
            .where(Attempt.solution_id == solution_id)
            .order_by(Attempt.created_at.desc())
        ).all()
        
    def count_by_user_and_task(self, user_id: int, task_id: int) -> int:
        query = (
            select(func.count())

            .select_from(Attempt)
            .join(Solution, Solution.id == Attempt.solution_id)
            .where(
                Solution.user_id == user_id,
                Solution.task_id == task_id,
            )
        )

        return self.db.execute(query).scalar_one()
def get_attempt_repository(db: Session = Depends(session_generator)):
    return AttemptRepository(db)