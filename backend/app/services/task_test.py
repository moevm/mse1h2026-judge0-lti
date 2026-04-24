from typing import List
from fastapi.params import Depends

from app.repositories.task_test import TaskTestRepository, get_task_test_repository
from app.repositories.task import TaskRepository, get_task_repository
from app.database.models import TaskTest
from app.schemas.task_test import TaskTestCreate, TaskTestFileSchema, TaskTestPatch
from app.services.task import TaskNotFoundException


class TaskTestNotFoundException(Exception):
    pass


class TaskTestService:
    def __init__(self, repo: TaskTestRepository, task_repo: TaskRepository) -> None:
        self.repo = repo
        self.task_repo = task_repo

    def get_tests(self, task_id: int):
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException
        return self.repo.get_by_task_id(task_id)

    def create_test(self, task_id: int, body: TaskTestCreate):
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException
        test = TaskTest(
            title=body.title, stdin=body.stdin, stdout=body.stdout, task_id=task_id
        )
        self.repo.add(test)
        self.repo.flush()
        return test

    def update_test(self, task_id: int, test_id: int, body: TaskTestPatch):
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException
        test = self.repo.get_by_id(test_id)
        if not test:
            raise TaskTestNotFoundException
        if test.task_id != task_id:
            raise TaskNotFoundException
        data = body.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(test, key, value)
        self.repo.save(test)
        return test

    def delete_test(self, task_id: int, test_id: int) -> None:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException
        test = self.repo.get_by_id(test_id)
        if not test:
            raise TaskTestNotFoundException
        if test.task_id != task_id:
            raise TaskTestNotFoundException
        self.repo.delete(test)

    def create_tests_bulk(self, task_id, body: TaskTestFileSchema):
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException
        tests = [
            TaskTest(
                title=t.title,
                task_id=task.id,
                stdin=t.stdin,
                stdout=t.stdout,
            )
            for t in body.tests
        ]
        self.repo.add_all(tests)
        self.repo.flush()
        return tests

def get_task_test_service(
    repo: TaskTestRepository = Depends(get_task_test_repository),
    task_repo: TaskRepository = Depends(get_task_repository),
) -> TaskTestService:
    return TaskTestService(repo, task_repo)
