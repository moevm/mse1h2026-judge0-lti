from fastapi import Depends
from sqlalchemy import select

from sqlalchemy.orm import Session

from app.database.models import Attempt
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

def get_attempt_repository(db: Session = Depends(session_generator)):
    return AttemptRepository(db)