from fastapi import Depends
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.tasks import (
    InvalidLanguageException,
    TaskAttemptsExceededException,
    TaskNotFoundException,
)
from app.database.database import session_generator
from app.schemas.check import CheckRequest, ResultRequest
from app.services.judge import JudgeService, get_judge_service
from app.repositories.task import TaskRepository, get_task_repository
from app.repositories.language import LanguageRepository, get_language_repository
from app.repositories.attempt import AttemptRepository, get_attempt_repository
from app.repositories.solution import SolutionRepository, get_solution_repository
from app.database.models import Solution, Attempt
from app.repositories.module_session import (
    ModuleSessionRepository,
    get_module_session_repository,
)
from app.core.exceptions.module_session import ModuleSessionNotActiveException


@dataclass
class CheckResult:
    success: bool
    passed: int
    total: int
    attempts_used: int
    max_attempts: int | None
    error: str | None = None
    comment: str | None = None


@dataclass
class AttemptsInfo:
    attempts_used: int
    max_attempts: int | None


@dataclass
class SubmitContext:
    tokens: list[str]
    task_id: int
    user_id: int
    solution_id: int
    language_id: int
    language: str


class CheckService:
    def __init__(
        self,
        db: AsyncSession,
        task_repo: TaskRepository,
        lang_repo: LanguageRepository,
        solution_repo: SolutionRepository,
        attempt_repo: AttemptRepository,
        judge: JudgeService,
        module_session_repo: ModuleSessionRepository,
    ) -> None:
        self.db = db
        self.task_repo = task_repo
        self.lang_repo = lang_repo
        self.solution_repo = solution_repo
        self.attempt_repo = attempt_repo
        self.judge = judge
        self.module_session_repo = module_session_repo

    async def get_attempts_info(self, task_id: int, user_id: int) -> AttemptsInfo:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException()

        attempts_used = await self.attempt_repo.count_by_user_and_task(user_id, task_id)
        return AttemptsInfo(attempts_used=attempts_used, max_attempts=task.max_attempts)

    async def submit(
        self, task_id: int, user_id: int, body: CheckRequest
    ) -> SubmitContext:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException()

        module_links = getattr(task, "module_links", None)
        if module_links:
            active_found = False
            for link in module_links:
                module_id = getattr(link, "module_id", None)
                if module_id is None:
                    continue
                active = await self.module_session_repo.get_active_session(
                    user_id, module_id
                )
                if active:
                    active_found = True
                    break
            if not active_found:
                raise ModuleSessionNotActiveException()

        attempts_used = await self.attempt_repo.count_by_user_and_task(user_id, task_id)
        if task.max_attempts is not None and attempts_used >= task.max_attempts:
            raise TaskAttemptsExceededException()

        language = await self.lang_repo.get_language_by_name(body.language)
        allowed = {lang.language for lang in task.languages}
        if not language or language.language not in allowed:
            raise InvalidLanguageException()

        solution = await self.solution_repo.get(user_id, task_id)
        if not solution:
            solution = Solution(
                user_id=user_id, task_id=task_id, is_solved=False, score=0
            )
            solution = await self.solution_repo.create(solution)
            await self.db.flush()
            await self.db.commit()

        tokens = await self.judge.submit_batch(
            source_code=body.code,
            language_id=language.id,
            tests=[{"stdin": t.stdin, "stdout": t.stdout} for t in task.tests],
            timeout=task.timeout,
        )

        return SubmitContext(
            tokens=tokens,
            task_id=task_id,
            user_id=user_id,
            solution_id=solution.id,
            language_id=language.id,
            language=body.language,
        )

    async def get_result(
        self, task_id: int, user_id: int, body: ResultRequest
    ) -> CheckResult | None:
        """Возвращает None если тесты ещё не готовы."""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException()

        results = await self.judge.fetch_batch(body.tokens)

        if not all(r["status"]["id"] > 2 for r in results):
            return None

        tests = task.tests
        total = len(tests)
        passed = 0
        failed_idx = None

        for i, result in enumerate(results):
            expected = (tests[i].stdout or "").strip()
            stdout = (result.get("stdout") or "").strip()
            if result["status"]["id"] == 3 and stdout == expected:
                passed += 1
            elif failed_idx is None:
                failed_idx = i

        score = (passed * 100) // total if total > 0 else 0

        if failed_idx is not None:
            r = results[failed_idx]
            if r["status"]["id"] == 3:
                status = "Wrong Answer"
                comment = (
                    f'Тест "{tests[failed_idx].title}" не прошёл. '
                    f'Ожидалось: "{(tests[failed_idx].stdout or "").strip()}", '
                    f'получено: "{(r.get("stdout") or "").strip()}"'
                )
            else:
                status = r["status"]["description"]
                comment = f'Тест "{tests[failed_idx].title}" — {status}'

            final_result = CheckResult(
                success=False,
                passed=passed,
                total=total,
                comment=comment,
                attempts_used=0,
                max_attempts=task.max_attempts,
            )
            attempt_data = {
                "is_solved": False,
                "status": status,
                "message": comment,
                "score": score,
                **self._extract_meta(r),
            }
        else:
            final_result = CheckResult(
                success=True,
                passed=passed,
                total=total,
                attempts_used=0,
                max_attempts=task.max_attempts,
            )
            attempt_data = {
                "is_solved": True,
                "status": "Accepted",
                "message": "Все тесты пройдены успешно",
                "score": 100,
                **self._extract_meta(results[0] if results else {}),
            }

        solution = await self.solution_repo.get_by_id(body.solution_id)
        if score > solution.score:
            solution.score = score
        if not solution.is_solved and passed == total:
            solution.is_solved = True

        attempt = Attempt(
            solution_id=body.solution_id,
            source_code=body.code,
            language=body.language,
            is_solved=attempt_data["is_solved"],
            status=attempt_data["status"],
            exit_code=attempt_data.get("exit_code"),
            stdout=attempt_data.get("stdout"),
            stderr=attempt_data.get("stderr"),
            compile_output=attempt_data.get("compile_output"),
            memory_kb=attempt_data.get("memory_kb"),
            time_ms=attempt_data.get("time_ms"),
            message=attempt_data.get("message"),
            score=attempt_data.get("score"),
        )
        await self.attempt_repo.create(attempt)
        await self.db.commit()

        attempts_used = await self.attempt_repo.count_by_user_and_task(user_id, task_id)
        final_result.attempts_used = attempts_used

        return final_result

    def _extract_meta(self, result: dict) -> dict:
        return {
            "exit_code": result.get("exit_code"),
            "stdout": result.get("stdout"),
            "stderr": result.get("stderr"),
            "compile_output": result.get("compile_output"),
            "memory_kb": int(result["memory"]) if result.get("memory") else None,
            "time_ms": (
                int(float(result["time"]) * 1000) if result.get("time") else None
            ),
        }


def get_check_service(
    db: AsyncSession = Depends(session_generator),
    task_repo: TaskRepository = Depends(get_task_repository),
    lang_repo: LanguageRepository = Depends(get_language_repository),
    solution_repo: SolutionRepository = Depends(get_solution_repository),
    attempt_repo: AttemptRepository = Depends(get_attempt_repository),
    judge: JudgeService = Depends(get_judge_service),
    module_session_repo: ModuleSessionRepository = Depends(
        get_module_session_repository
    ),
) -> CheckService:
    return CheckService(
        db,
        task_repo,
        lang_repo,
        solution_repo,
        attempt_repo,
        judge,
        module_session_repo,
    )
