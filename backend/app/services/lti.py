from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import session_generator
from app.database.models import User, UserTypeEnum
from app.repositories.user import UserRepository, get_user_repository


def map_role(roles: str) -> UserTypeEnum:
    if "Instructor" in roles:
        return UserTypeEnum.teacher
    return UserTypeEnum.student


class LtiService:
    def __init__(self, db: AsyncSession, repo: UserRepository):
        self.db = db
        self.repo = repo

    async def upsert_user(
        self, user_id: int, username: str, full_name: str, roles: str
    ) -> User:
        role = map_role(roles)

        user = await self.repo.get_by_id(user_id)

        if not user:
            user = User(id=user_id, username=username, full_name=full_name, role=role)
            await self.repo.add(user)
        else:
            user.username = username
            user.full_name = full_name
            user.role = role
        await self.db.commit()
        await self.db.refresh(user)
        return user


def get_lti_service(
    db: AsyncSession = Depends(session_generator),
    repo: UserRepository = Depends(get_user_repository),
) -> LtiService:
    return LtiService(db, repo)
