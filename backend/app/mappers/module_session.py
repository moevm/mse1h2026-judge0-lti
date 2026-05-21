from datetime import datetime, timezone

from app.database.models import ModuleSession
from app.schemas.module_session import ModuleSessionResponse, ModuleSessionBase

class ModuleSessionMapper:

    @staticmethod
    def to_response(session: ModuleSession | None) -> ModuleSessionResponse:
        return ModuleSessionResponse(
            session=ModuleSessionBase.model_validate(session) if session else None,
            server_time_now=datetime.now(timezone.utc),
        )
