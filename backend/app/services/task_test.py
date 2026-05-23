from typing import List
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.tasks import TaskNotFoundException, TaskTestNotFoundException
from app.database.database import session_generator
from app.repositories.task_test import TaskTestRepository, get_task_test_repository
from app.repositories.task import TaskRepository, get_task_repository
from app.database.models import TaskTest, Task
from app.schemas.task_test import TaskTestCreate, TaskTestFileSchema, TaskTestPatch


class TaskTestService:
    def __init__(self, db: AsyncSession, repo: TaskTestRepository, task_repo: TaskRepository) -> None:
        self.db = db
        self.repo = repo
        self.task_repo = task_repo

    async def get_tests(self, task_id: int):
        task = await self._get_task_or_raise(task_id)
        return await self.repo.get_by_task_id(task_id)

    async def create_test(self, task_id: int, body: TaskTestCreate) -> TaskTest:
        await self._get_task_or_raise(task_id)
        test = TaskTest(
            title=body.title, stdin=body.stdin, stdout=body.stdout, task_id=task_id
        )
        await self.repo.add(test)
        await self.db.commit()
        await self.db.refresh(test)
        return test

    async def update_test(self, task_id: int, test_id: int, body: TaskTestPatch):
        await self._get_task_or_raise(task_id)
        test = await self._get_test_or_raise(task_id, test_id)
        data = body.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(test, key, value)
        await self.db.commit()
        await self.db.refresh(test)
        return test

    async def delete_test(self, task_id: int, test_id: int) -> None:
        await self._get_task_or_raise(task_id)
        test = await self._get_test_or_raise(task_id, test_id)
        await self.repo.delete(test)
        await self.db.commit()

    async def create_tests_bulk(self, task_id, body: TaskTestFileSchema):
        task = await self._get_task_or_raise(task_id)
        tests = [
            TaskTest(
                title=t.title,
                task_id=task.id,
                stdin=t.stdin,
                stdout=t.stdout,
            )
            for t in body.tests
        ]
        await self.repo.add_all(tests)
        await self.db.commit()
        return tests

    async def _get_task_or_raise(self, task_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException(f"Задача {task_id} не найдена")
        return task

    async  def _get_test_or_raise(self, task_id: int, test_id: int) -> TaskTest:
        test = await self.repo.get_by_id_and_task(test_id, task_id)
        if not test:
            raise TaskTestNotFoundException(
                f"Тест {test_id} не найден в задаче {task_id}"
            )
        return test


def get_task_test_service(
    db: AsyncSession = Depends(session_generator),
    repo: TaskTestRepository = Depends(get_task_test_repository),
    task_repo: TaskRepository = Depends(get_task_repository),
) -> TaskTestService:
    return TaskTestService(db, repo, task_repo)
