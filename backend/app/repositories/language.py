from typing import List

from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import session_generator
from app.database.models import Language


class LanguageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Language]:
        query = select(Language)
        return self.db.scalars(query).all()

    def get_language_by_name(self, language_name: str) -> Language | None:
        query = select(Language).where(Language.language == language_name)
        return self.db.scalars(query).first()

    def get_by_names(self, names: list[str]) -> list[Language]:
        query = select(Language).where(Language.language.in_(names))
        return self.db.scalars(query).all()


def get_language_repository(
    db: Session = Depends(session_generator),
) -> LanguageRepository:
    return LanguageRepository(db)
