from fastapi import Depends
from app.repositories.analytics import AnalyticsRepository, get_analytics_repository
from app.schemas.analytics import (
    UserModuleResponse, UserTaskResponse, AttemptResponse,
    UserModulesFilter, UserTasksFilter, AttemptsFilter
)
from datetime import datetime

class UserNotFoundException(Exception):
    pass


class ModuleNotFoundException(Exception):
    pass


class AttemptNotFoundException(Exception):
    pass


class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    def get_user_modules(self, user_id: int, filters: UserModulesFilter) -> list[UserModuleResponse]:
        modules = self.repo.get_user_modules(user_id)

        result = []
        for module in modules:
            task_count = self.repo.get_module_task_count(module.id)
            result.append(UserModuleResponse(
                id=module.id,
                title=module.title,
                description=module.description,
                task_count=task_count,
                created_at=module.created_at,
            ))

        # фильтрация
        if filters.search:
            s = filters.search.lower()
            result = [r for r in result if s in r.title.lower()]

        # сортировка
        reverse = filters.sort_order == "desc"
        if filters.sort_by == "name":
            result.sort(key=lambda x: x.title.lower(), reverse=reverse)
        elif filters.sort_by == "tasks_count":
            result.sort(key=lambda x: x.task_count, reverse=reverse)
        elif filters.sort_by == "created_at":
            result.sort(key=lambda x: x.created_at, reverse=reverse)

        return result

    def get_user_tasks_in_module(
        self, user_id: int, module_id: int, filters: UserTasksFilter
    ) -> list[UserTaskResponse]:
        rows = self.repo.get_user_tasks_in_module(user_id, module_id)

        result = []
        for task, solution in rows:
            attempt_count = self.repo.get_attempt_count(user_id, task.id)
            last_attempt_at = self.repo.get_last_attempt_at(user_id, task.id)
            test_count = self.repo.get_task_test_count(task.id)

            result.append(UserTaskResponse(
                id=task.id,
                title=task.title,
                attempt_count=attempt_count,
                is_solved=solution.is_solved,
                last_attempt_at=last_attempt_at,
                test_count=test_count,
            ))

        # фильтрация
        if filters.search:
            s = filters.search.lower()
            result = [r for r in result if s in r.title.lower()]

        if filters.attempt_count_min is not None:
            result = [r for r in result if r.attempt_count >= filters.attempt_count_min]

        if filters.status == "passed":
            result = [r for r in result if r.is_solved]
        elif filters.status == "failed":
            result = [r for r in result if not r.is_solved]

        if filters.last_attempt_from:
            result = [r for r in result if r.last_attempt_at and r.last_attempt_at >= filters.last_attempt_from]

        if filters.last_attempt_to:
            result = [r for r in result if r.last_attempt_at and r.last_attempt_at <= filters.last_attempt_to]

        if filters.test_count_min is not None:
            result = [r for r in result if r.test_count >= filters.test_count_min]

        # сортировка
        reverse = filters.sort_order == "desc"
        sort_key = {
            "title": lambda x: x.title.lower(),
            "attempt_count": lambda x: x.attempt_count,
            "last_attempt_at": lambda x: x.last_attempt_at or datetime.min,
            "test_count": lambda x: x.test_count,
        }.get(filters.sort_by)
        if sort_key:
            result.sort(key=sort_key, reverse=reverse)

        return result

    def get_task_attempts(
        self, task_id: int, user_id: int, filters: AttemptsFilter
    ) -> list[AttemptResponse]:
        attempts = self.repo.get_task_attempts(task_id, user_id)

        result = [AttemptResponse(
            id=a.id,
            message=a.message,
            language=a.language,
            memory_mb=a.memory_mb,
            time_ms=a.time_ms,
            is_solved=a.is_solved,
            created_at=a.created_at,
        ) for a in attempts]

        if filters.status == "passed":
            result = [r for r in result if r.is_solved]
        elif filters.status == "failed":
            result = [r for r in result if not r.is_solved]

        if filters.language:
            result = [r for r in result if r.language and filters.language.lower() in r.language.lower()]

        if filters.memory_min is not None:
            result = [r for r in result if r.memory_mb and r.memory_mb >= filters.memory_min]

        if filters.memory_max is not None:
            result = [r for r in result if r.memory_mb and r.memory_mb <= filters.memory_max]

        if filters.time_min is not None:
            result = [r for r in result if r.time_ms and r.time_ms >= filters.time_min]

        if filters.time_max is not None:
            result = [r for r in result if r.time_ms and r.time_ms <= filters.time_max]

        if filters.from_date:
            result = [r for r in result if r.created_at >= filters.from_date]

        if filters.to_date:
            result = [r for r in result if r.created_at <= filters.to_date]

        return result

    def get_attempt_by_id(self, attempt_id: int) -> AttemptResponse:
        attempt = self.repo.get_attempt_by_id(attempt_id)
        if not attempt:
            raise AttemptNotFoundException
        return AttemptResponse(
            id=attempt.id,
            message=attempt.message,
            language=attempt.language,
            memory_mb=attempt.memory_mb,
            time_ms=attempt.time_ms,
            is_solved=attempt.is_solved,
            created_at=attempt.created_at,
        )


    def is_my_student(self, teacher_id: int, student_id: int) -> bool:
        modules = self.repo.get_teacher_modules(teacher_id)
        for module in modules:
            tasks = self.repo.get_module_tasks(module.id)
            for task in tasks:
                if self.repo.has_solution(student_id, task.id):
                    return True
        return False


def get_analytics_service(
    repo: AnalyticsRepository = Depends(get_analytics_repository)
) -> AnalyticsService:
    return AnalyticsService(repo)
