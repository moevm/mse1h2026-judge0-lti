from fastapi.params import Depends
from app.repositories.task import TaskRepository, get_task_repository
from app.database.models import Task


class TaskNotFoundException(Exception):
    pass


class TaskService:
    def __init__(self, repo: TaskRepository) -> None:
        self.repo = repo

    def get_task_by_id(self, task_id: int) -> Task:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException
        return task


def get_task_service(
    repo: TaskRepository = Depends(get_task_repository),
) -> TaskService:
    return TaskService(repo)
