from unittest.mock import MagicMock, patch

with patch("app.database.database.create_engine"), \
    patch("app.database.models.Base.metadata.create_all"):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.database.database import session_generator

client = TestClient(app)


def make_language():
    lang = MagicMock()
    lang.language = "python"
    lang.id = 71
    return lang


def make_task(language):
    task = MagicMock()
    task.id = 1
    task.timeout = 10
    task.languages = [language]
    task.tests_pipeline = [
        {"title": "Тест 1", "input": {"stdin": "2 3"}, "output": {"stdout": "5"}}
    ]
    return task


def make_db():
    language = make_language()
    task = make_task(language)

    db = MagicMock()

    task_query = MagicMock()
    task_query.filter.return_value.first.return_value = task

    lang_query = MagicMock()
    lang_query.filter.return_value.first.return_value = language

    db.query.side_effect = [task_query, lang_query]
    return db


def test_check_solution_mock():
    def override():
        yield make_db()

    app.dependency_overrides[session_generator] = override

    with patch("app.services.check.CheckService._submit_to_judge0") as mock_submit:
        mock_submit.return_value = {
            "stdout": "5",
            "stderr": None,
            "status": {"id": 3, "description": "Accepted"}
        }

        response = client.post("/check/1", json={
            "language": "python",
            "code": "print(2+3)",
            "submitted_at": "2026-03-16T10:00:00"
        })

        print("\nСтатус:", response.status_code)
        print("Ответ:", response.json())
        assert response.status_code == 200
        assert response.json()["success"] == True


def test_check_solution_fail():
    def override():
        yield make_db()

    app.dependency_overrides[session_generator] = override

    with patch("app.services.check.CheckService._submit_to_judge0") as mock_submit:
        mock_submit.return_value = {
            "stdout": "999",
            "stderr": None,
            "status": {"id": 3, "description": "Accepted"}
        }

        response = client.post("/check/1", json={
            "language": "python",
            "code": "print(999)",
            "submitted_at": "2026-03-16T10:00:00"
        })

        print("\nСтатус:", response.status_code)
        print("Ответ:", response.json())
        assert response.status_code == 200
        assert response.json()["success"] == False