from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.database.database import session_generator
from app.database.models import ModuleSession


class ModuleSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, session: ModuleSession) -> ModuleSession:
        self.db.add(session)
        self.db.flush()
        self.db.refresh(session)
        return session

    def get_active_session(self, user_id: int, module_id: int):
        query = (
            select(ModuleSession)
            .where(
                ModuleSession.user_id == user_id,
                ModuleSession.module_id == module_id,
                ModuleSession.finished_at.is_(None),
                ModuleSession.expires_at > func.now(),
            )
            .order_by(ModuleSession.started_at.desc())
            .limit(1)
        )

        return self.db.execute(query).scalar_one_or_none()

    def count_finished_sessions(self, user_id: int, module_id: int) -> int:
        query = (
            select(func.count())
            .select_from(ModuleSession)
            .where(
                ModuleSession.user_id == user_id,
                ModuleSession.module_id == module_id,
                or_(
                    ModuleSession.finished_at.is_not(None),
                    ModuleSession.expires_at <= func.now(),
                ),
            )
        )

        return self.db.execute(query).scalar_one()


def get_module_session_repository(db: Session = Depends(session_generator)):
    return ModuleSessionRepository(db)
