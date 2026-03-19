from unittest.mock import MagicMock, patch
from datetime import datetime

with patch("app.database.database.create_engine"), \
    patch("app.database.models.Base.metadata.create_all"):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.database.database import session_generator
    from app.services.module import get_module_service

client = TestClient(app)


def make_task(task_id: int):
    task = MagicMock()
    task.id = task_id
    task.title = f"Задача {task_id}"
    task.description = "Описание"
    task.timeout = 10
    task.created_at = datetime(2024, 1, 1)
    task.updated_at = None
    task.languages = [MagicMock(language="python")]
    return task


def make_module(module_id: int, tasks: list):
    module = MagicMock()
    module.id = module_id
    module.title = f"Модуль {module_id}"
    module.description = "Описание модуля"
    module.created_at = datetime(2024, 1, 1)
    module.updated_at = None
    module.tasks = tasks
    return module


def make_module_service(modules=None, module=None, tasks=None, not_found=False):
    service = MagicMock()
    if not_found:
        from app.services.module import ModuleNotFoundException
        service.get_all_modules.side_effect = ModuleNotFoundException
        service.get_module_by_id.side_effect = ModuleNotFoundException
        service.get_module_tasks.side_effect = ModuleNotFoundException
    else:
        service.get_all_modules.return_value = modules or []
        service.get_module_by_id.return_value = module
        service.get_module_tasks.return_value = tasks or []
    return service


# GET /modules/
def test_get_modules():
    tasks = [make_task(1), make_task(2)]
    modules = [make_module(1, tasks)]

    app.dependency_overrides[get_module_service] = lambda: make_module_service(modules=modules)

    response = client.get("/modules/")
    print("\nСтатус:", response.status_code)
    print("Ответ:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 1
    assert data[0]["tasks"] == [1, 2]


# GET /modules/{id}
def test_get_module_by_id():
    tasks = [make_task(1)]
    module = make_module(1, tasks)

    app.dependency_overrides[get_module_service] = lambda: make_module_service(module=module)

    response = client.get("/modules/1")
    print("\nСтатус:", response.status_code)
    print("Ответ:", response.json())
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["tasks"] == [1]


# GET /modules/{id} — не найден
def test_get_module_not_found():
    app.dependency_overrides[get_module_service] = lambda: make_module_service(not_found=True)

    response = client.get("/modules/999")
    print("\nСтатус:", response.status_code)
    print("Ответ:", response.json())
    assert response.status_code == 404
    assert response.json()["detail"] == "Модуль не найден"


# GET /modules/{id}/tasks
def test_get_module_tasks():
    tasks = [make_task(1), make_task(2)]

    app.dependency_overrides[get_module_service] = lambda: make_module_service(tasks=tasks)

    response = client.get("/modules/1/tasks")
    print("\nСтатус:", response.status_code)
    print("Ответ:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 1


# GET /modules/{id}/tasks — модуль не найден
def test_get_module_tasks_not_found():
    app.dependency_overrides[get_module_service] = lambda: make_module_service(not_found=True)

    response = client.get("/modules/999/tasks")
    print("\nСтатус:", response.status_code)
    print("Ответ:", response.json())
    assert response.status_code == 404