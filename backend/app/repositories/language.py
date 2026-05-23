from typing import List

from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import session_generator
from app.database.models import Language


class LanguageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Language]:
        result = await self.db.execute(select(Language))
        return result.scalars().all()

    async def get_language_by_name(self, language_name: str) -> Language | None:
        result = await self.db.execute(
            select(Language).where(Language.language == language_name)
        )
        return result.scalars().first()

    async def get_by_names(self, names: List[str]) -> List[Language]:
        result = await self.db.execute(
            select(Language).where(Language.language.in_(names))
        )
        return result.scalars().all()


def get_language_repository(
    db: AsyncSession = Depends(session_generator),
) -> LanguageRepository:
    return LanguageRepository(db)
