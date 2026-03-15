from unittest.mock import MagicMock, patch

with patch("app.database.database.create_engine"), \
    patch("app.database.models.Base.metadata.create_all"):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.database.database import session_generator


def override_session():
    task = MagicMock()
    task.id = 1
    task.title = "Сложение чисел"
    task.description = "Сложи два числа"
    task.timeout = 10
    task.created_at = "2024-01-01T00:00:00"
    task.updated_at = None
    task.languages = [MagicMock(language="python")]

    db = MagicMock()
    db.query().filter().first.return_value = task
    yield db


app.dependency_overrides[session_generator] = override_session
client = TestClient(app)


def test_get_task_success():
    response = client.get("/tasks/1")
    print("\n--- test_get_task_success ---")
    print("Статус:", response.status_code)
    print("Заголовки:", dict(response.headers))
    print("Ответ:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Сложение чисел"
    assert "tests_pipeline" not in data
    print("Все проверки прошли")



def test_get_task_not_found():
    def override_empty():
        db = MagicMock()
        db.query().filter().first.return_value = None
        yield db

    app.dependency_overrides[session_generator] = override_empty
    response = client.get("/tasks/999")
    print("\n--- test_get_task_not_found ---")
    print("Статус:", response.status_code)
    print("Заголовки:", dict(response.headers))
    print("Ответ:", response.json())
    assert response.status_code == 404
    print("Все проверки прошли")