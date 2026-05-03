from fastapi import Depends
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session
from app.database.models import User, Solution
from app.database.database import session_generator
from app.schemas.user import UserFilter


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        return self.db.scalars(query).first()

    def add(self, user: User):
        self.db.add(user)

    def get_all(self, filters: UserFilter) -> list[User]:
        query = select(User)

        if not filters.include_deleted:
            query = query.where(User.deleted_at == None)

        if filters.search:
            s = f"%{filters.search}%"
            query = query.where(
                or_(
                    User.full_name.ilike(s),
                    User.username.ilike(s),
                )
            )
        return self.db.scalars(query).all()

    def get_solved_count(self, user_id: int) -> int:
        query = select(func.count()).select_from(Solution).where(
            Solution.user_id == user_id,
            Solution.is_solved == True
        )
        return self.db.scalar(query)


def get_user_repository(db: Session = Depends(session_generator)) -> UserRepository:
    return UserRepository(db)
