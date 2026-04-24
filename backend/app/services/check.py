from fastapi import Depends
from dataclasses import dataclass
from app.schemas.check import CheckRequest
from app.services.judge import JudgeService, get_judge_service
from app.repositories.task import TaskRepository, get_task_repository
from app.repositories.language import LanguageRepository, get_language_repository


@dataclass
class CheckResult:
    success: bool
    passed: int
    total: int
    error: str | None = None
    comment: str | None = None


class TaskNotFoundException(Exception):
    pass


class InvalidLanguageException(Exception):
    pass


class CheckService:
    def __init__(
        self,
        task_repo: TaskRepository,
        lang_repo: LanguageRepository,
        judge: JudgeService,
    ) -> None:
        self.task_repo = task_repo
        self.lang_repo = lang_repo
        self.judge = judge

    def check_solution(self, task_id: int, body: CheckRequest) -> CheckResult:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException

        language = self.lang_repo.get_language_by_name(body.language)
        language_names = [lang.language for lang in task.languages]
        if not language or language.language not in language_names:
            raise InvalidLanguageException

        tests = task.tests
        total = len(tests)
        passed = 0
        for test in tests:
            stdin = test.stdin or ""
            expected = (test.stdout or "").strip()
            result = self.judge.submit(body.code, language.id, stdin, task.timeout)

            if result["status"]["id"] not in (3, 4):
                return CheckResult(
                    success=False,
                    passed=passed,
                    total=total,
                    error=result.get("stderr")
                    or result.get("compile_output")
                    or "Ошибка выполнения",
                    comment=f'Тест "{test["title"]}" — {result["status"]["description"]}',
                )

            stdout = (result.get("stdout") or "").strip()
            if stdout == expected:
                passed += 1
            else:
                return CheckResult(
                    success=False,
                    passed=passed,
                    total=total,
                    error=None,
                    comment=f'Тест "{test["title"]}" не прошёл. Ожидалось: "{expected}", получено: "{stdout}"',
                )

        return CheckResult(success=True, passed=passed, total=total, comment=None)


def get_check_service(
    task_repo: TaskRepository = Depends(get_task_repository),
    lang_repo: LanguageRepository = Depends(get_language_repository),
    judge: JudgeService = Depends(get_judge_service),
) -> CheckService:
    return CheckService(task_repo, lang_repo, judge)
