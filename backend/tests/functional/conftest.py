import os
import pytest
import time
from typing import AsyncGenerator
from httpx import AsyncClient

API_URL = os.getenv("API_URL", "http://localhost:8000")


@pytest.fixture
async def client() -> AsyncGenerator:
    async with AsyncClient(base_url=API_URL, timeout=30.0) as client:
        yield client


@pytest.fixture
async def admin_auth(client):
    """Авторизованный админ (админ должен быть создан в БД бекенда)"""
    time.sleep(0.5)
    login_response = await client.post(
        "/api/auth/login", json={"username": "admin", "password": "adminpass"}
    )
    assert login_response.status_code == 200, "Admin user must exist in database"
    access_token = login_response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {access_token}"
    return client


@pytest.fixture
async def create_task_via_api(admin_auth):
    """Создание задачи через API"""

    async def _create_task(title: str, description: str, timeout: int, languages: list):
        response = await admin_auth.post(
            "/api/tasks/",
            json={
                "title": title,
                "description": description,
                "timeout": timeout,
                "languages": languages,
            },
        )
        assert response.status_code == 200
        return response.json()

    return _create_task


@pytest.fixture
async def create_module_via_api(admin_auth):
    """Создание модуля через API"""

    async def _create_module(title: str, description: str):
        response = await admin_auth.post(
            "/api/modules/", json={"title": title, "description": description}
        )
        assert response.status_code == 200
        return response.json()

    return _create_module


@pytest.fixture
async def add_task_to_module_via_api(admin_auth):
    """Добавление задачи в модуль через API"""

    async def _add_task(module_id: int, task_ids: list):
        response = await admin_auth.post(
            f"/api/modules/{module_id}/tasks", json={"task_ids": task_ids}
        )
        assert response.status_code == 200
        return response.json()

    return _add_task


@pytest.fixture
async def create_test_via_api(admin_auth):
    """Создание теста для задачи через API"""

    async def _create_test(task_id: int, title: str, stdin: str, stdout: str):
        response = await admin_auth.post(
            f"/api/tasks/{task_id}/tests",
            json={
                "title": title,
                "stdin": stdin,
                "stdout": stdout,
            },
        )
        assert response.status_code == 200
        return response.json()

    return _create_test