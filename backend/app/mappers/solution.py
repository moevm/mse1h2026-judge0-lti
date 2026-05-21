from typing import Optional
from app.database.models import Solution, Attempt
from app.schemas.solution import SolutionWithUserResponse
from app.schemas.attempt import AttemptResponse


class SolutionMapper:

    @staticmethod
    def to_solution_with_user_response(solution: Solution) -> SolutionWithUserResponse:
        return SolutionWithUserResponse(
            id=solution.id,
            task_id=solution.task_id,
            user_id=solution.user_id,
            username=solution.user.username if solution.user else None,
            full_name=solution.user.full_name if solution.user else None,
            is_solved=solution.is_solved,
            score=solution.score,
            created_at=solution.created_at,
            updated_at=solution.updated_at,
        )

    @staticmethod
    def to_attempt_response(attempt: Attempt) -> AttemptResponse:
        return AttemptResponse(
            id=attempt.id,
            solution_id=attempt.solution_id,
            source_code=attempt.source_code,
            language=attempt.language,
            status=attempt.status,
            exit_code=attempt.exit_code,
            stdout=attempt.stdout,
            stderr=attempt.stderr,
            compile_output=attempt.compile_output,
            memory_kb=attempt.memory_kb,
            time_ms=attempt.time_ms,
            is_solved=attempt.is_solved,
            message=attempt.message,
            score=attempt.score,
            created_at=attempt.created_at,
        )
