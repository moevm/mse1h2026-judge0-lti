from fastapi import Depends
from dataclasses import dataclass
from app.core.exceptions.tasks import InvalidLanguageException, TaskNotFoundException
from app.schemas.check import CheckRequest
from app.services.judge import JudgeService, get_judge_service
from app.repositories.task import TaskRepository, get_task_repository
from app.repositories.language import LanguageRepository, get_language_repository
from app.repositories.attempt import AttemptRepository, get_attempt_repository
from app.repositories.solution import SolutionRepository, get_solution_repository
from app.database.models import Solution, Attempt


@dataclass
class CheckResult:
    success: bool
    passed: int
    total: int
    error: str | None = None
    comment: str | None = None


class CheckService:
    def __init__(
        self,
        task_repo: TaskRepository,
        lang_repo: LanguageRepository,
        solution_repo: SolutionRepository,
        attempt_repo: AttemptRepository,
        judge: JudgeService,
    ) -> None:
        self.task_repo = task_repo
        self.lang_repo = lang_repo
        self.solution_repo = solution_repo
        self.attempt_repo = attempt_repo
        self.judge = judge

    async def check_solution(
        self, task_id: int, user_id: int, body: CheckRequest
    ) -> CheckResult:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException()

        language = self.lang_repo.get_language_by_name(body.language)
        allowed = {lang.language for lang in task.languages}
        if not language or language.language not in allowed:
            raise InvalidLanguageException()

        solution = self.solution_repo.get(user_id, task_id)
        if not solution:
            solution = Solution(
                user_id=user_id,
                task_id=task_id,
                is_solved=False,
                score=0,
            )
            solution = self.solution_repo.create(solution)

        tests = task.tests
        total = len(tests)
        passed = 0
        final_result = None
        last_attempt_data = None

        for test in tests:
            result = await self.judge.submit(
                source_code=body.code,
                language_id=language.id,
                stdin=test.stdin or "",
                timeout=task.timeout,
            )

            expected = (test.stdout or "").strip()
            stdout = (result.get("stdout") or "").strip()

            if result["status"]["id"] not in (3, 4):
                final_result = CheckResult(
                    success=False,
                    passed=passed,
                    total=total,
                    error=result.get("stderr")
                    or result.get("compile_output")
                    or "Ошибка выполнения",
                    comment=f'Тест "{test.title}" — {result["status"]["description"]}',
                )
                last_attempt_data = {
                    "status": result["status"]["description"],
                    "exit_code": result.get("exit_code"),
                    "stdout": result.get("stdout"),
                    "stderr": result.get("stderr"),
                    "compile_output": result.get("compile_output"),
                    "memory_kb": (
                        int(result.get("memory"))
                        if result.get("memory") is not None
                        else None
                    ),
                    "time_ms": (
                        int(float(result.get("time", 0)) * 1000)
                        if result.get("time") is not None
                        else None
                    ),
                    "is_solved": False,
                    "message": final_result.comment,
                    "score": (passed * 100) // total if total > 0 else 0,
                }
                break

            if stdout == expected:
                passed += 1
            else:
                final_result = CheckResult(
                    success=False,
                    passed=passed,
                    total=total,
                    error=None,
                    comment=f'Тест "{test.title}" не прошёл. Ожидалось: "{expected}", получено: "{stdout}"',
                )
                last_attempt_data = {
                    "status": "Wrong Answer",
                    "exit_code": result.get("exit_code"),
                    "stdout": result.get("stdout"),
                    "stderr": result.get("stderr"),
                    "compile_output": result.get("compile_output"),
                    "memory_kb": (
                        int(result.get("memory"))
                        if result.get("memory") is not None
                        else None
                    ),
                    "time_ms": (
                        int(float(result.get("time", 0)) * 1000)
                        if result.get("time") is not None
                        else None
                    ),
                    "is_solved": False,
                    "message": final_result.comment,
                    "score": (passed * 100) // total if total > 0 else 0,
                }
                break

        if final_result is None:
            final_result = CheckResult(
                success=True, passed=passed, total=total, comment=None
            )
            last_attempt_data = {
                "status": "Accepted",
                "exit_code": 0,
                "stdout": None,
                "stderr": None,
                "compile_output": None,
                "memory_kb": None,
                "time_ms": None,
                "is_solved": True,
                "message": "Все тесты пройдены успешно",
                "score": (passed * 100) // total if total > 0 else 0,
            }

        new_score = (passed * 100) // total if total > 0 else 0

        if new_score > solution.score:
            solution.score = new_score

        if not solution.is_solved and passed == total:
            solution.is_solved = True

        self.solution_repo.save(solution)

        attempt = Attempt(
            solution_id=solution.id,
            source_code=body.code,
            language=body.language,
            is_solved=last_attempt_data["is_solved"],
            status=last_attempt_data["status"],
            exit_code=last_attempt_data.get("exit_code"),
            stdout=last_attempt_data.get("stdout"),
            stderr=last_attempt_data.get("stderr"),
            compile_output=last_attempt_data.get("compile_output"),
            memory_kb=last_attempt_data.get("memory_kb"),
            time_ms=last_attempt_data.get("time_ms"),
            message=last_attempt_data.get("message"),
            score=last_attempt_data.get("score"),
        )
        self.attempt_repo.create(attempt)

        return final_result


def get_check_service(
    task_repo: TaskRepository = Depends(get_task_repository),
    lang_repo: LanguageRepository = Depends(get_language_repository),
    solution_repo: SolutionRepository = Depends(get_solution_repository),
    attempt_repo: AttemptRepository = Depends(get_attempt_repository),
    judge: JudgeService = Depends(get_judge_service),
) -> CheckService:
    return CheckService(task_repo, lang_repo, solution_repo, attempt_repo, judge)