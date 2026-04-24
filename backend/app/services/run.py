from fastapi.params import Depends
from app.services.judge import JudgeService
from app.schemas.run import RunRequest
from app.services.judge import get_judge_service
from app.repositories.language import LanguageRepository, get_language_repository


class LanguageNotFoundException(Exception):
    pass


class RunService:
    def __init__(self, lang_repo: LanguageRepository, judge: JudgeService) -> None:
        self.lang_repo = lang_repo
        self.judge = judge

    def run_code(self, body: RunRequest):
        language = self.lang_repo.get_language_by_name(body.language)
        if not language:
            raise LanguageNotFoundException("Language not found")
        return self.judge.submit(body.code, language.id, body.stdin, 5)


def get_run_service(
    lang_repo: LanguageRepository = Depends(get_language_repository),
    judge: JudgeService = Depends(get_judge_service),
) -> RunService:
    return RunService(lang_repo, judge)
