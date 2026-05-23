from fastapi import Depends
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, Solution
from app.database.database import session_generator
from app.schemas.user import UserFilter

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.db.get(User, user_id)

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalars().first()

    async def add(self, user: User) -> None:
        self.db.add(user)

    async def get_all(self, filters: UserFilter) -> list[User]:
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
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_solved_count(self, user_id: int) -> int:
        result = await self.db.scalar(
            select(func.count()).select_from(Solution).where(
                Solution.user_id == user_id,
                Solution.is_solved == True,
            )
        )
        return result or 0

def get_user_repository(db: AsyncSession = Depends(session_generator)) -> UserRepository:
    return UserRepository(db)
