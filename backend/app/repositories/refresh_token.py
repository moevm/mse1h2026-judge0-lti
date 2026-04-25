from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.database.database import session_generator
from app.database.models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, token: RefreshToken):
        self.db.add(token)

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        query = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return self.db.scalars(query).first()

    def delete_all_by_user(self, user_id: int):
        self.db.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))

    def revoke(self, token: RefreshToken):
        token.revoked = True


def get_refresh_token_repository(
    db: Session = Depends(session_generator),
) -> RefreshTokenRepository:
    return RefreshTokenRepository(db)
