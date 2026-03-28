from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.models import User
from app.database.database import session_generator


class UserNotFoundException(Exception):
    pass


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundException
        return user


def get_user_service(db: Session = Depends(session_generator)) -> UserService:
    return UserService(db)
