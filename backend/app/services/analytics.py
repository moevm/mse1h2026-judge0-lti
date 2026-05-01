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
        return self.repo.get_user_tasks_in_module(user_id, module_id, filters)

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
