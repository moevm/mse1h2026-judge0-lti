from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import session_generator
from app.database.models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, token: RefreshToken):
        self.db.add(token)

    def flush(self):
        self.db.flush()


def get_refresh_token_repository(
    db: Session = Depends(session_generator),
) -> RefreshTokenRepository:
    return RefreshTokenRepository(db)