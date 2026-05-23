from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import session_generator
from app.database.models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, token: RefreshToken) -> None:
        self.db.add(token)

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalars().first()

    async def delete_all_by_user(self, user_id: int) -> None:
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )

    async def revoke(self, token: RefreshToken) -> None:
        token.revoked = True


def get_refresh_token_repository(
    db: AsyncSession = Depends(session_generator),
) -> RefreshTokenRepository:
    return RefreshTokenRepository(db)
