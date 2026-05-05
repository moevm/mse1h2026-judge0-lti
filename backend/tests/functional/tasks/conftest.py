from datetime import datetime, timezone

import pytest
from typing import AsyncGenerator
from fastapi import FastAPI, APIRouter
from httpx import AsyncClient, ASGITransport

from app.routers import tasks as tasks_router
from app.services.task import TaskService
from app.services.task_test import TaskTestService
from tests.mocks import (
    MockTaskRepository,
    MockTaskTestRepository,
    MockLanguageRepository,
    MockTask,
    MockTaskTest,
)
from tests.mocks.models import MockUser


@pytest.fixture
def mock_task_repo():
    repo = MockTaskRepository()
    return repo


@pytest.fixture
def mock_task_test_repo():
    return MockTaskTestRepository()


@pytest.fixture
def mock_language_repo():
    return MockLanguageRepository()


@pytest.fixture
def task_service(mock_task_repo, mock_language_repo):
    """Сервис задач с мок-репозиториями"""
    return TaskService(
        repo=mock_task_repo,
        lang_repo=mock_language_repo,
    )


@pytest.fixture
def task_test_service(mock_task_test_repo, mock_task_repo):
    """Сервис тестов задач с мок-репозиториями"""
    return TaskTestService(
        repo=mock_task_test_repo,
        task_repo=mock_task_repo,
    )


@pytest.fixture
def app_with_tasks(task_service, task_test_service):
    """Приложение с tasks роутерами"""
    app = FastAPI()
    api_router = APIRouter(prefix="/api")
    api_router.include_router(tasks_router.router)
    app.include_router(api_router)

    # Override зависимостей
    def get_mock_task_service():
        return task_service

    def get_mock_task_test_service():
        return task_test_service

    app.dependency_overrides[tasks_router.get_task_service] = get_mock_task_service
    app.dependency_overrides[tasks_router.get_task_test_service] = (
        get_mock_task_test_service
    )

    # Мокаем get_current_admin
    from app.core.dependencies import get_current_admin

    async def mock_get_current_admin():
        user = MockUser(username="admin", password_hash="hashed_pass", role="admin")
        user.id = 1
        return user

    app.dependency_overrides[get_current_admin] = mock_get_current_admin

    return app


@pytest.fixture
async def tasks_client(app_with_tasks) -> AsyncGenerator:
    """HTTP клиент для тестов tasks"""
    transport = ASGITransport(app=app_with_tasks)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def create_test_task(mock_task_repo, mock_language_repo):
    """Создание тестовой задачи - использует настоящую SQLAlchemy Task"""
    from app.database.models import Task

    def _create_task(
        title: str = "Test Task",
        description: str = "Task Description",
        timeout: int = 30,
        language_names: list = None,
    ):
        if language_names is None:
            language_names = ["python", "javascript"]

        task = Task()
        task.id = None
        task.title = title
        task.description = description
        task.timeout = timeout
        task.created_at = datetime.now(timezone.utc)
        task.updated_at = datetime.now(timezone.utc)

        task.languages = []
        for lang_name in language_names:
            lang = mock_language_repo.get_language_by_name(lang_name)
            if lang:
                task.languages.append(lang)

        task.tests = []

        mock_task_repo.add(task)
        return task

    return _create_task


@pytest.fixture
def create_test_test(mock_task_test_repo):
    """Создание тестового теста для задачи"""

    def _create_test(
        task_id: int,
        title: str = "Test Case",
        stdin: str = "",
        stdout: str = "expected output",
    ):
        test = MockTaskTest(title=title, stdin=stdin, stdout=stdout, task_id=task_id)
        mock_task_test_repo.add(test)
        return test

    return _create_test
