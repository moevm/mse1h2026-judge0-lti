from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import session_generator
from app.database.models import ModuleSession


class ModuleSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, module_session: ModuleSession) -> ModuleSession:
        self.db.add(module_session)
        self.db.flush()
        self.db.refresh(module_session)
        return module_session

    def get_active_session(self, user_id: int, module_id: int):
        return (
            self.db.query(ModuleSession)
            .filter(
                ModuleSession.user_id == user_id,
                ModuleSession.module_id == module_id,
            )
            .order_by(ModuleSession.started_at.desc())
            .first()
        )

    def count_sessions(self, user_id: int, module_id: int) -> int:
        return (
            self.db.query(ModuleSession)
            .filter(
                ModuleSession.user_id == user_id,
                ModuleSession.module_id == module_id,
            )
            .count()
        )


def get_module_session_repository(db: Session = Depends(session_generator)):
    return ModuleSessionRepository(db)
