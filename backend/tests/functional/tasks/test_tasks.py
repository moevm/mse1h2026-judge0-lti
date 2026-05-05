import pytest
import json


class TestGetTasks:
    """Тесты GET /api/tasks/"""
    @pytest.mark.asyncio
    async def test_get_tasks_empty(self, tasks_client):
        """Получение списка задач когда их нет"""
        response = await tasks_client.get("/api/tasks/")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_tasks_with_data(self, tasks_client, create_test_task):
        """Получение списка задач с данными"""
        create_test_task(title="Task 1", description="Desc 1")
        create_test_task(title="Task 2", description="Desc 2")

        response = await tasks_client.get("/api/tasks/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Task 1"
        assert data[1]["title"] == "Task 2"

    @pytest.mark.asyncio
    async def test_get_tasks_with_search_filter(self, tasks_client, create_test_task):
        """Фильтрация задач по поиску"""
        create_test_task(title="Python Basics", description="Learn Python")
        create_test_task(title="Java Basics", description="Learn Java")
        create_test_task(title="Advanced Python", description="Advanced Python")

        response = await tasks_client.get("/api/tasks/?search=Python")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        titles = [t["title"] for t in data]
        assert "Python Basics" in titles
        assert "Advanced Python" in titles

    @pytest.mark.asyncio
    async def test_get_tasks_with_timeout_filter(self, tasks_client, create_test_task):
        """Фильтрация задач по timeout"""
        create_test_task(title="Fast Task", timeout=10)
        create_test_task(title="Medium Task", timeout=30)
        create_test_task(title="Slow Task", timeout=60)

        response = await tasks_client.get("/api/tasks/?timeout_from=20&timeout_to=50")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Medium Task"
        assert data[0]["timeout"] == 30


class TestGetTask:
    """Тесты GET /api/tasks/{task_id}"""
    @pytest.mark.asyncio
    async def test_get_task_success(self, tasks_client, create_test_task):
        """Получение задачи по ID"""
        task = create_test_task(
            title="Specific Task", description="Specific Desc", timeout=45
        )

        response = await tasks_client.get(f"/api/tasks/{task.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id
        assert data["title"] == "Specific Task"
        assert data["description"] == "Specific Desc"
        assert data["timeout"] == 45
        assert "languages" in data

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, tasks_client):
        """Получение несуществующей задачи"""
        response = await tasks_client.get("/api/tasks/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Задача не найдена"


class TestCreateTask:
    """Тесты POST /api/tasks/"""
    @pytest.mark.asyncio
    async def test_create_task_success(self, tasks_client):
        """Успешное создание задачи"""
        response = await tasks_client.post(
            "/api/tasks/",
            json={
                "title": "New Task",
                "description": "Task Description",
                "timeout": 30,
                "languages": ["python", "javascript"],
                "tests": [
                    {"title": "Test 1", "stdin": "", "stdout": "output1"},
                    {"title": "Test 2", "stdin": "input", "stdout": "output2"},
                ],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "Task Description"
        assert data["timeout"] == 30
        assert "python" in data["languages"]
        assert "javascript" in data["languages"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_task_invalid_language(self, tasks_client):
        """Создание задачи с невалидным языком"""
        response = await tasks_client.post(
            "/api/tasks/",
            json={
                "title": "Task",
                "description": "Desc",
                "timeout": 30,
                "languages": ["invalid_language"],
            },
        )

        assert response.status_code == 400
        assert "недопустимый язык" in response.json()["detail"].lower()


class TestPatchTask:
    """Тесты PATCH /api/tasks/{task_id}"""
    @pytest.mark.asyncio
    async def test_patch_task_success(self, tasks_client, create_test_task):
        """Успешное обновление задачи"""
        task = create_test_task(
            title="Original Title", description="Original Desc", timeout=30
        )

        response = await tasks_client.patch(
            f"/api/tasks/{task.id}", json={"title": "Updated Title", "timeout": 60}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Original Desc"
        assert data["timeout"] == 60

    @pytest.mark.asyncio
    async def test_patch_task_update_languages(self, tasks_client, create_test_task):
        """Обновление языков задачи"""
        task = create_test_task(language_names=["python"])

        response = await tasks_client.patch(
            f"/api/tasks/{task.id}",
            json={"languages": ["python", "javascript", "java"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert "python" in data["languages"]
        assert "javascript" in data["languages"]
        assert "java" in data["languages"]

    @pytest.mark.asyncio
    async def test_patch_task_not_found(self, tasks_client):
        """Обновление несуществующей задачи"""
        response = await tasks_client.patch("/api/tasks/999", json={"title": "Updated"})

        assert response.status_code == 404
        assert response.json()["detail"] == "Задача не найдена"

    @pytest.mark.asyncio
    async def test_patch_task_invalid_language(self, tasks_client, create_test_task):
        """Обновление с невалидным языком"""
        task = create_test_task()

        response = await tasks_client.patch(
            f"/api/tasks/{task.id}", json={"languages": ["invalid_lang"]}
        )

        assert response.status_code == 400
        assert "недопустимый язык" in response.json()["detail"].lower()


class TestDeleteTask:
    """Тесты DELETE /api/tasks/{task_id}"""
    @pytest.mark.asyncio
    async def test_delete_task_success(self, tasks_client, create_test_task):
        """Успешное удаление задачи"""
        task = create_test_task(title="To Delete")

        response = await tasks_client.delete(f"/api/tasks/{task.id}")

        assert response.status_code == 204

        get_response = await tasks_client.get(f"/api/tasks/{task.id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, tasks_client):
        """Удаление несуществующей задачи"""
        response = await tasks_client.delete("/api/tasks/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Задача не найдена"


class TestGetTaskTests:
    """Тесты GET /api/tasks/{task_id}/tests"""

    @pytest.mark.asyncio
    async def test_get_tests_empty(self, tasks_client, create_test_task):
        """Получение тестов задачи когда их нет"""
        task = create_test_task()

        response = await tasks_client.get(f"/api/tasks/{task.id}/tests")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_tests_success(
        self, tasks_client, create_test_task, create_test_test
    ):
        """Получение тестов задачи"""
        task = create_test_task()
        create_test_test(task.id, title="Test 1", stdout="output1")
        create_test_test(task.id, title="Test 2", stdout="output2")

        response = await tasks_client.get(f"/api/tasks/{task.id}/tests")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Test 1"
        assert data[1]["title"] == "Test 2"

    @pytest.mark.asyncio
    async def test_get_tests_task_not_found(self, tasks_client):
        """Получение тестов несуществующей задачи"""
        response = await tasks_client.get("/api/tasks/999/tests")

        assert response.status_code == 404
        assert response.json()["detail"] == "Задача не найдена"


class TestCreateTaskTest:
    """Тесты POST /api/tasks/{task_id}/tests"""
    @pytest.mark.asyncio
    async def test_create_test_success(self, tasks_client, create_test_task):
        """Успешное создание теста"""
        task = create_test_task()

        response = await tasks_client.post(
            f"/api/tasks/{task.id}/tests",
            json={
                "title": "New Test",
                "stdin": "input data",
                "stdout": "expected output",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Test"
        assert data["stdin"] == "input data"
        assert data["stdout"] == "expected output"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_test_task_not_found(self, tasks_client):
        """Создание теста для несуществующей задачи"""
        response = await tasks_client.post(
            "/api/tasks/999/tests", json={"title": "Test", "stdin": "", "stdout": "out"}
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Задача не найдена"


class TestDeleteTaskTest:
    """Тесты DELETE /api/tasks/{task_id}/tests/{test_id}"""

    @pytest.mark.asyncio
    async def test_delete_test_success(
        self, tasks_client, create_test_task, create_test_test
    ):
        """Успешное удаление теста"""
        task = create_test_task()
        test = create_test_test(task.id, title="To Delete")

        response = await tasks_client.delete(f"/api/tasks/{task.id}/tests/{test.id}")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_test_task_not_found(self, tasks_client):
        """Удаление теста из несуществующей задачи"""
        response = await tasks_client.delete("/api/tasks/999/tests/1")

        assert response.status_code == 404
        assert response.json()["detail"] == "Задача не найдена"

    @pytest.mark.asyncio
    async def test_delete_test_not_found(self, tasks_client, create_test_task):
        """Удаление несуществующего теста"""
        task = create_test_task()

        response = await tasks_client.delete(f"/api/tasks/{task.id}/tests/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Тест не найден"


class TestPatchTaskTest:
    """Тесты PATCH /api/tasks/{task_id}/tests/{test_id}"""
    @pytest.mark.asyncio
    async def test_patch_test_success(
        self, tasks_client, create_test_task, create_test_test
    ):
        """Успешное обновление теста"""
        task = create_test_task()
        test = create_test_test(task.id, title="Original", stdin="", stdout="old")

        response = await tasks_client.patch(
            f"/api/tasks/{task.id}/tests/{test.id}",
            json={"title": "Updated", "stdout": "new output"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"
        assert data["stdout"] == "new output"
        assert data["stdin"] == ""

    @pytest.mark.asyncio
    async def test_patch_test_task_not_found(self, tasks_client):
        """Обновление теста в несуществующей задаче"""
        response = await tasks_client.patch(
            "/api/tasks/999/tests/1", json={"title": "Updated"}
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Задача не найдена"

    @pytest.mark.asyncio
    async def test_patch_test_not_found(self, tasks_client, create_test_task):
        """Обновление несуществующего теста"""
        task = create_test_task()

        response = await tasks_client.patch(
            f"/api/tasks/{task.id}/tests/999", json={"title": "Updated"}
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Тест не найден"


class TestImportTests:
    """Тесты POST /api/tasks/{task_id}/tests/import"""
    @pytest.mark.asyncio
    async def test_import_tests_success(self, tasks_client, create_test_task):
        """Успешный импорт тестов из JSON"""
        task = create_test_task()

        tests_data = {
            "tests": [
                {"title": "Test 1", "stdin": "", "stdout": "out1"},
                {"title": "Test 2", "stdin": "input", "stdout": "out2"},
                {"title": "Test 3", "stdin": "data", "stdout": "out3"},
            ]
        }

        files = {"file": ("tests.json", json.dumps(tests_data), "application/json")}

        response = await tasks_client.post(
            f"/api/tasks/{task.id}/tests/import", files=files
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["title"] == "Test 1"
        assert data[1]["title"] == "Test 2"
        assert data[2]["title"] == "Test 3"

    @pytest.mark.asyncio
    async def test_import_tests_invalid_json(self, tasks_client, create_test_task):
        """Импорт с невалидным JSON"""
        task = create_test_task()

        files = {"file": ("tests.json", "invalid json {", "application/json")}

        response = await tasks_client.post(
            f"/api/tasks/{task.id}/tests/import", files=files
        )

        assert response.status_code == 400
        assert "Некорректный JSON" in response.json()["detail"]


class TestFullTaskFlow:
    """Полный цикл работы с задачами"""
    @pytest.mark.asyncio
    async def test_full_task_flow(self, tasks_client):

        create_response = await tasks_client.post(
            "/api/tasks/",
            json={
                "title": "Flow Task",
                "description": "Test flow",
                "timeout": 30,
                "languages": ["python", "javascript"],
            },
        )
        assert create_response.status_code == 200
        task_id = create_response.json()["id"]

        test1 = await tasks_client.post(
            f"/api/tasks/{task_id}/tests",
            json={"title": "Test 1", "stdin": "", "stdout": "output1"},
        )
        assert test1.status_code == 200
        test1_id = test1.json()["id"]

        test2 = await tasks_client.post(
            f"/api/tasks/{task_id}/tests",
            json={"title": "Test 2", "stdin": "input", "stdout": "output2"},
        )
        assert test2.status_code == 200
        get_tests = await tasks_client.get(f"/api/tasks/{task_id}/tests")
        assert len(get_tests.json()) == 2

        patch_test = await tasks_client.patch(
            f"/api/tasks/{task_id}/tests/{test1_id}",
            json={"title": "Updated Test", "stdout": "new_output"},
        )
        assert patch_test.status_code == 200
        assert patch_test.json()["title"] == "Updated Test"

        patch_task = await tasks_client.patch(
            f"/api/tasks/{task_id}", json={"title": "Updated Flow Task", "timeout": 60}
        )
        assert patch_task.status_code == 200
        assert patch_task.json()["title"] == "Updated Flow Task"

        delete_test = await tasks_client.delete(
            f"/api/tasks/{task_id}/tests/{test1_id}"
        )
        assert delete_test.status_code == 204

        get_tests_after = await tasks_client.get(f"/api/tasks/{task_id}/tests")
        assert len(get_tests_after.json()) == 1

        delete_task = await tasks_client.delete(f"/api/tasks/{task_id}")
        assert delete_task.status_code == 204

        get_task = await tasks_client.get(f"/api/tasks/{task_id}")
        assert get_task.status_code == 404
