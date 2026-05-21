from datetime import datetime, timezone, timedelta

from fastapi import Depends

from app.core.exceptions.module_session import ModuleAttemptsExceededException
from app.database.models import ModuleSession
from app.repositories.module_session import (
    ModuleSessionRepository,
    get_module_session_repository,
)
from app.schemas.auth import TokenUser
from app.services.module import ModuleService, get_module_service


class ModuleSessionService:
    def __init__(self, repo: ModuleSessionRepository, module_service: ModuleService):
        self.repo = repo
        self.module_service = module_service

    def start_session(self, module_id: int, user: TokenUser) -> ModuleSession:
        module = self.module_service.get_module_by_id(module_id)
        active_session = self.repo.get_active_session(user.user_id, module_id)
        if active_session:
            return active_session
        used_sessions = self.repo.count_used_sessions(user.user_id, module_id)
        if used_sessions >= module.max_attempts:
            raise ModuleAttemptsExceededException()
        now = datetime.now(timezone.utc)
        session = ModuleSession(
            module_id=module_id,
            user_id=user.user_id,
            started_at=now,
            expires_at=now + timedelta(seconds=module.duration_seconds),
        )
        return self.repo.add(session)

    def get_session(self, module_id: int, user: TokenUser):
        return self.repo.get_active_session(user.user_id, module_id)


def get_module_session_service(
    repo: ModuleSessionRepository = Depends(get_module_session_repository),
    module_service: ModuleService = Depends(get_module_service),
) -> ModuleSessionService:
    return ModuleSessionService(repo, module_service)
