from app.database.models import Module, Task, Solution, Attempt
from app.schemas.analytics import UserModuleResponse, UserTaskResponse, AttemptResponse
from typing import Optional
from datetime import datetime


class AnalyticsMapper:

    @staticmethod
    def to_module_response(module: Module, task_count: int) -> UserModuleResponse:
        return UserModuleResponse(
            id=module.id,
            title=module.title,
            description=module.description,
            task_count=task_count,
            created_at=module.created_at,
        )

    @staticmethod
    def to_task_response(
        task: Task,
        solution: Solution,
        attempt_count: int,
        last_attempt_at: Optional[datetime],
        test_count: int
    ) -> UserTaskResponse:
        return UserTaskResponse(
            id=task.id,
            title=task.title,
            attempt_count=attempt_count,
            is_solved=solution.is_solved,
            last_attempt_at=last_attempt_at,
            test_count=test_count,
        )

    @staticmethod
    def to_attempt_response(attempt: Attempt) -> AttemptResponse:
        return AttemptResponse(
            id=attempt.id,
            message=attempt.message,
            language=attempt.language,
            memory_mb=attempt.memory_mb,
            time_ms=attempt.time_ms,
            is_solved=attempt.is_solved,
            created_at=attempt.created_at,
        )
