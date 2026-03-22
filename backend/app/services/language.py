from typing import List

from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.database.models import Language
from app.database.database import session_generator


class LanguageService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all_languages(self) -> List[Language]:
        languages = self.db.query(Language).all()
        return languages


def get_language_service(db: Session = Depends(session_generator)) -> LanguageService:
    return LanguageService(db=db)
