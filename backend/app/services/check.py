import os
import base64
import requests
from fastapi import Depends
from sqlalchemy.orm import Session
from dataclasses import dataclass

from app.database.models import Task, Language
from app.schemas.check import CheckRequest, CheckResponse
from app.database.database import session_generator

JUDGE0_URL = os.getenv("JUDGE0_URL", "http://judge0_server:2358")
MOCK_JUDGE0 = os.getenv("MOCK_JUDGE0", "false") == "true"


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


class Judge0Exception(Exception):
    pass


class CheckService:
    def __init__(self, db: Session):
        self.db = db

    def _submit_to_judge0(
        self, source_code: str, language_id: int, stdin: str, timeout: int
    ):
        if MOCK_JUDGE0:
            return {
                "stdout": "mocked",
                "stderr": None,
                "status": {"id": 3, "description": "Accepted"},
            }
        # кодируем код и stdin в base64
        encoded_code = base64.b64encode(source_code.encode("utf-8")).decode()
        encoded_stdin = base64.b64encode(stdin.encode("utf-8")).decode()

        response = requests.post(
            f"{JUDGE0_URL}/submissions?wait=true",
            json={
                "source_code": encoded_code,
                "language_id": language_id,
                "stdin": encoded_stdin,
                "cpu_time_limit": timeout,
                "base64_encoded": True,  # говорим Judge0 что всё в base64
            },
        )

        if response.status_code not in (200, 201):
            raise Judge0Exception

        result = response.json()
        # декодируем ответ из base64
        if result.get("stdout"):
            result["stdout"] = base64.b64decode(result["stdout"]).decode("utf-8")
        if result.get("stderr"):
            result["stderr"] = base64.b64decode(result["stderr"]).decode("utf-8")
        if result.get("compile_output"):
            result["compile_output"] = base64.b64decode(
                result["compile_output"]
            ).decode("utf-8")

        return result

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

        for test in tests:
            stdin = test["input"]["stdin"]
            expected = test["output"]["stdout"].strip()
            result = self._submit_to_judge0(body.code, language.id, stdin, task.timeout)

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

        return CheckResult(
            success=True, passed=passed, total=total, comment=None
        )


def get_check_service(db: Session = Depends(session_generator)) -> CheckService:
    return CheckService(db)
