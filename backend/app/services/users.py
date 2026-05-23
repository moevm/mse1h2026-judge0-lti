from datetime import datetime, timezone
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.users import UserNotFoundException
from app.database.database import session_generator
from app.database.models import User
from app.repositories.user import UserRepository, get_user_repository
from app.schemas.user import UserFilter, UserUpdateRequest


class UserService:
    def __init__(self, db: AsyncSession, repo: UserRepository):
        self.db = db
        self.repo = repo

    async def get_by_id(self, user_id: int) -> User:
        user = await self._get_user_or_raise(user_id)
        return user

    async def get_all(self, filters: UserFilter) -> list[tuple[User, int]]:
        users = await self.repo.get_all(filters)
        return [(user, await self.repo.get_solved_count(user.id)) for user in users]

    async def get_with_solved_count(self, user_id: int) -> tuple[User, int]:
        user = await self._get_user_or_raise(user_id)
        return user, await self.repo.get_solved_count(user_id)

    async def update(self, user_id: int, body: UserUpdateRequest) -> User:
        user = await self._get_user_or_raise(user_id)
        if body.full_name is not None:
            user.full_name = body.full_name
        if body.role is not None:
            user.role = body.role
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int):
        user = await self._get_user_or_raise(user_id)
        user.deleted_at = datetime.now(timezone.utc)
        await self.db.commit()

    async def _get_user_or_raise(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"Пользователь {user_id} не найден")
        return user


def get_user_service(
    db: AsyncSession = Depends(session_generator),
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(db, repo)
