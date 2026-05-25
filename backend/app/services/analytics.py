from fastapi import Depends

from app.core.exceptions.analytics import AttemptNotFoundException
from app.repositories.analytics import AnalyticsRepository, get_analytics_repository
from app.schemas.analytics import UserModulesFilter, UserTasksFilter, AttemptsFilter
from app.database.models import Attempt


class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    async def get_user_modules(self, user_id: int, filters: UserModulesFilter) -> list[tuple]:
        modules = await self.repo.get_user_modules(user_id, filters)
        result = []
        for module in modules:
            task_count = len(module.task_links)
            result.append((module, task_count))

        if filters.sort_by == "tasks_count":
            result.sort(key=lambda x: x[1], reverse=filters.sort_order == "desc")
        return result

    async def get_user_tasks_in_module(
        self, user_id: int, module_id: int, filters: UserTasksFilter
    ) -> list[tuple]:
        return await self.repo.get_user_tasks_in_module(user_id, module_id, filters)

    async def get_task_attempts(
        self, task_id: int, user_id: int, filters: AttemptsFilter
    ) -> list[Attempt]:
        return await self.repo.get_task_attempts(task_id, user_id, filters)

    async def get_attempt_by_id(self, attempt_id: int) -> Attempt:
        attempt = await self.repo.get_attempt_by_id(attempt_id)
        if not attempt:
            raise AttemptNotFoundException(f"Попытка {attempt_id} не найдена")
        return attempt

    async def is_my_student(self, teacher_id: int, student_id: int) -> bool:
        modules = await self.repo.get_teacher_modules(teacher_id)
        for module in modules:
            tasks = await self.repo.get_module_tasks(module.id)
            for task in tasks:
                if await self.repo.has_solution(student_id, task.id):
                    return True
        return False


def get_analytics_service(
    repo: AnalyticsRepository = Depends(get_analytics_repository),
) -> AnalyticsService:
    return AnalyticsService(repo)
