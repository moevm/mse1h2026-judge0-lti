from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.models import User
from app.database.database import session_generator


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def add(self, user: User):
        self.db.add(user)


def get_user_repository(db: Session = Depends(session_generator)) -> UserRepository:
    return UserRepository(db)
