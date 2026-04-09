from fastapi import Depends
from sqlalchemy.orm import Session
from dataclasses import dataclass

from app.database.models import Task, Language
from app.schemas.check import CheckRequest, CheckResponse
from app.database.database import session_generator
from app.services.judge import JudgeService, get_judge_service


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
    def __init__(self, db: Session, judge: JudgeService) -> None:
        self.db = db
        self.judge = judge

    def check_solution(self, task_id: int, body: CheckRequest) -> CheckResult:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise TaskNotFoundException

        language = (
            self.db.query(Language).filter(Language.language == body.language).first()
        )
        language_names = [lang.language for lang in task.languages]
        if not language or language.language not in language_names:
            raise InvalidLanguageException

        tests = task.tests_pipeline
        total = len(tests)
        passed = 0
        print("TEST", tests)
        for test in tests:
            stdin = test["input"].get("stdin", "")
            expected = test["output"]["stdout"].strip()
            result = self.judge.submit(body.code, language.id, stdin, task.timeout)
            print("RES", result)

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
    db: Session = Depends(session_generator),
    judge: JudgeService = Depends(get_judge_service),
) -> CheckService:
    return CheckService(db, judge)
