from typing import List
from fastapi.params import Depends
from app.database.models import Language
from app.repositories.language import LanguageRepository, get_language_repository


class LanguageService:
    def __init__(self, repo: LanguageRepository) -> None:
        self.repo = repo

    def get_all_languages(self) -> List[Language]:
        languages = self.repo.get_all()
        return languages


def get_language_service(
    repo: LanguageRepository = Depends(get_language_repository),
) -> LanguageService:
    return LanguageService(repo)
