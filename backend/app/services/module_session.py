from datetime import datetime, timezone, timedelta

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.module_session import ModuleAttemptsExceededException, ModuleSessionNotActiveException
from app.database.database import session_generator
from app.database.models import ModuleSession
from app.repositories.module_session import (
    ModuleSessionRepository,
    get_module_session_repository,
)
from app.schemas.auth import TokenUser
from app.services.module import ModuleService, get_module_service


class ModuleSessionService:
    def __init__(self, db: AsyncSession, repo: ModuleSessionRepository, module_service: ModuleService):
        self.db = db
        self.repo = repo
        self.module_service = module_service

    async def start_session(self, module_id: int, user: TokenUser) -> ModuleSession:
        module = await self.module_service.get_module_by_id(module_id)
        active = await self.repo.get_active_session(user.user_id, module_id)
        if active:
            return active
        used = await self.repo.count_finished_sessions(user.user_id, module_id)
        if module.max_attempts is not None and used >= module.max_attempts:
            raise ModuleAttemptsExceededException()
        now = datetime.now(timezone.utc)
        session = ModuleSession(
            module_id=module_id,
            user_id=user.user_id,
            started_at=now,
            expires_at=now + timedelta(seconds=module.duration_seconds)
            if module.duration_seconds is not None
            else None,
        )
        await self.repo.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session(self, module_id: int, user: TokenUser) -> ModuleSession | None:
        return await self.repo.get_active_session(user.user_id, module_id)

    async def finish_session(self, module_id: int, user: TokenUser) -> ModuleSession:
        session = await self.repo.get_active_session(user.user_id, module_id)
        if not session:
            raise ModuleSessionNotActiveException()
        await self.repo.finish_session(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session


def get_module_session_service(
    db: AsyncSession = Depends(session_generator),
    repo: ModuleSessionRepository = Depends(get_module_session_repository),
    module_service: ModuleService = Depends(get_module_service),
) -> ModuleSessionService:
    return ModuleSessionService(db, repo, module_service)
