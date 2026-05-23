from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy import and_, select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import session_generator
from app.database.models import ModuleSession

class ModuleSessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, session: ModuleSession) -> ModuleSession:
        self.db.add(session)
        return session

    async def get_active_session(self, user_id: int, module_id: int) -> ModuleSession | None:
        result = await self.db.execute(
            select(ModuleSession)
            .where(
                ModuleSession.user_id == user_id,
                ModuleSession.module_id == module_id,
                ModuleSession.finished_at.is_(None),
                or_(
                    ModuleSession.expires_at.is_(None),
                    ModuleSession.expires_at > func.now(),
                ),
            )
            .order_by(ModuleSession.started_at.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def count_finished_sessions(self, user_id: int, module_id: int) -> int:
        result = await self.db.scalar(
            select(func.count())
            .select_from(ModuleSession)
            .where(
                ModuleSession.user_id == user_id,
                ModuleSession.module_id == module_id,
                or_(
                    ModuleSession.finished_at.is_not(None),
                    and_(
                        ModuleSession.expires_at.is_not(None),
                        ModuleSession.expires_at <= func.now(),
                    ),
                ),
            )
        )
        return result or 0

    async def finish_session(self, session: ModuleSession) -> ModuleSession:
        session.finished_at = datetime.now(timezone.utc)
        return session


def get_module_session_repository(db: AsyncSession = Depends(session_generator)):
    return ModuleSessionRepository(db)
