from datetime import timezone, datetime
from fastapi import Depends
from app.repositories.analytics import AnalyticsRepository, get_analytics_repository
from app.schemas.analytics import UserModulesFilter, UserTasksFilter, AttemptsFilter
from app.database.models import Module, Task, Solution, Attempt


class AttemptNotFoundException(Exception):
    pass


class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    def get_user_modules(self, user_id: int, filters: UserModulesFilter) -> list[tuple]:
        modules = self.repo.get_user_modules(user_id, filters)
        result = []
        for module in modules:
            task_count = len(module.task_links)
            result.append((module, task_count))

        if filters.sort_by == "tasks_count":
            result.sort(
                key=lambda x: x[1],
                reverse=filters.sort_order == "desc"
            )
        return result

    def get_user_tasks_in_module(
        self, user_id: int, module_id: int, filters: UserTasksFilter
    ) -> list[tuple]:
        rows = self.repo.get_user_tasks_in_module(user_id, module_id, filters)
        if not rows:
            return []

        task_ids = [task.id for task, _ in rows]
        attempt_counts = self.repo.get_attempt_counts(user_id, task_ids)
        last_attempts = self.repo.get_last_attempts(user_id, task_ids)

        result = []
        for task, solution in rows:
            attempt_count = attempt_counts.get(task.id, 0)
            last_attempt_at = last_attempts.get(task.id)
            test_count = len(task.tests)

            if filters.attempt_count_min is not None and attempt_count < filters.attempt_count_min:
                continue
            if filters.last_attempt_from and (not last_attempt_at or last_attempt_at < filters.last_attempt_from):
                continue
            if filters.last_attempt_to and (not last_attempt_at or last_attempt_at > filters.last_attempt_to):
                continue
            if filters.test_count_min is not None and test_count < filters.test_count_min:
                continue

            result.append((task, solution, attempt_count, last_attempt_at, test_count))

        sort_key = {
            "title": lambda x: x[0].title.lower(),
            "attempt_count": lambda x: x[2],
            "last_attempt_at": lambda x: x[3] or datetime.min.replace(tzinfo=timezone.utc),
            "test_count": lambda x: x[4],
        }.get(filters.sort_by)
        if sort_key:
            result.sort(key=sort_key, reverse=filters.sort_order == "desc")

        return result

    def get_task_attempts(
        self, task_id: int, user_id: int, filters: AttemptsFilter
    ) -> list[Attempt]:
        return self.repo.get_task_attempts(task_id, user_id, filters)

    def get_attempt_by_id(self, attempt_id: int) -> Attempt:
        attempt = self.repo.get_attempt_by_id(attempt_id)
        if not attempt:
            raise AttemptNotFoundException
        return attempt

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
