import pytest
import json

pytestmark = pytest.mark.integration


class TestGetTasks:
    """Тесты GET /api/tasks/"""

    @pytest.mark.asyncio
    async def test_get_tasks_empty(self, client):
        """Получение списка задач когда их нет"""
        response = await client.get("/api/tasks/")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_tasks_with_data(self, client, create_test_task):
        """Получение списка задач с данными"""
        await create_test_task(title="Task 1", description="Desc 1")
        await create_test_task(title="Task 2", description="Desc 2")

        response = await client.get("/api/tasks/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_tasks_with_search_filter(self, client, create_test_task):
        """Фильтрация задач по поиску"""
        await create_test_task(title="Python Basics", description="Learn Python")
        await create_test_task(title="Java Basics", description="Learn Java")
        await create_test_task(title="Advanced Python", description="Advanced Python")

        response = await client.get("/api/tasks/?search=advanced")
        print(response.json())
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    @pytest.mark.asyncio
    async def test_get_tasks_with_timeout_filter(self, client, create_test_task):
        """Фильтрация задач по timeout"""
        await create_test_task(title="Fast Task", timeout=10)
        await create_test_task(title="Medium Task", timeout=30)
        await create_test_task(title="Slow Task", timeout=60)

        response = await client.get("/api/tasks/?timeout_from=20&timeout_to=50")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Medium Task"
        assert data[0]["timeout"] == 30


class TestGetTask:
    """Тесты GET /api/tasks/{task_id}"""

    @pytest.mark.asyncio
    async def test_get_task_success(self, client, create_test_task):
        """Получение задачи по ID"""
        task = await create_test_task(
            title="Specific Task", description="Specific Desc", timeout=45
        )

        response = await client.get(f"/api/tasks/{task.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id
        assert data["title"] == "Specific Task"
        assert data["description"] == "Specific Desc"
        assert data["timeout"] == 45
        assert "languages" in data

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client):
        """Получение несуществующей задачи"""
        response = await client.get("/api/tasks/999")

        assert response.status_code == 404


class TestCreateTask:
    """Тесты POST /api/tasks/"""

    @pytest.mark.asyncio
    async def test_create_task_success(self, client):
        """Успешное создание задачи"""
        response = await client.post(
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
        print(response.json())
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Task"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_task_invalid_language(self, client):
        """Создание задачи с невалидным языком"""
        response = await client.post(
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
    async def test_patch_task_success(self, client, create_test_task):
        """Успешное обновление задачи"""
        task = await create_test_task(
            title="Original Title", description="Original Desc", timeout=30
        )

        response = await client.patch(
            f"/api/tasks/{task.id}", json={"title": "Updated Title", "timeout": 60}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Original Desc"
        assert data["timeout"] == 60

    @pytest.mark.asyncio
    async def test_patch_task_update_languages(self, client, create_test_task):
        """Обновление языков задачи"""
        # Создаем задачу с одним языком
        task = await create_test_task(language_names=["python"])

        response = await client.patch(
            f"/api/tasks/{task.id}",
            json={"languages": ["python", "javascript", "java"]},
        )
        print(response.json())
        assert response.status_code == 200
        data = response.json()
        assert "python" in data["languages"]
        assert "javascript" in data["languages"]
        assert "java" in data["languages"]

    @pytest.mark.asyncio
    async def test_patch_task_not_found(self, client):
        """Обновление несуществующей задачи"""
        response = await client.patch("/api/tasks/999", json={"title": "Updated"})

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_patch_task_invalid_language(self, client, create_test_task):
        """Обновление с невалидным языком"""
        task = await create_test_task()

        response = await client.patch(
            f"/api/tasks/{task.id}", json={"languages": ["invalid_lang"]}
        )

        assert response.status_code == 400
        assert "недопустимый язык" in response.json()["detail"].lower()


class TestDeleteTask:
    """Тесты DELETE /api/tasks/{task_id}"""

    @pytest.mark.asyncio
    async def test_delete_task_success(self, client, create_test_task):
        """Успешное удаление задачи"""
        task = await create_test_task(title="To Delete")

        response = await client.delete(f"/api/tasks/{task.id}")

        assert response.status_code == 204

        get_response = await client.get(f"/api/tasks/{task.id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, client):
        """Удаление несуществующей задачи"""
        response = await client.delete("/api/tasks/999")

        assert response.status_code == 404


class TestGetTaskTests:
    """Тесты GET /api/tasks/{task_id}/tests"""

    @pytest.mark.asyncio
    async def test_get_tests_empty(self, client, create_test_task):
        """Получение тестов задачи когда их нет"""
        task = await create_test_task()

        response = await client.get(f"/api/tasks/{task.id}/tests")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_tests_success(self, client, create_test_task, create_test_test):
        """Получение тестов задачи"""
        task = await create_test_task()
        await create_test_test(task.id, title="Test 1", stdout="output1")
        await create_test_test(task.id, title="Test 2", stdout="output2")

        response = await client.get(f"/api/tasks/{task.id}/tests")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Test 1"
        assert data[1]["title"] == "Test 2"

    @pytest.mark.asyncio
    async def test_get_tests_task_not_found(self, client):
        """Получение тестов несуществующей задачи"""
        response = await client.get("/api/tasks/999/tests")

        assert response.status_code == 404


class TestCreateTaskTest:
    """Тесты POST /api/tasks/{task_id}/tests"""

    @pytest.mark.asyncio
    async def test_create_test_success(self, client, create_test_task):
        """Успешное создание теста"""
        task = await create_test_task()

        response = await client.post(
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
    async def test_create_test_task_not_found(self, client):
        """Создание теста для несуществующей задачи"""
        response = await client.post(
            "/api/tasks/999/tests", json={"title": "Test", "stdin": "", "stdout": "out"}
        )

        assert response.status_code == 404


class TestDeleteTaskTest:
    """Тесты DELETE /api/tasks/{task_id}/tests/{test_id}"""

    @pytest.mark.asyncio
    async def test_delete_test_success(
        self, client, create_test_task, create_test_test
    ):
        """Успешное удаление теста"""
        task = await create_test_task()
        test = await create_test_test(task.id, title="To Delete")

        response = await client.delete(f"/api/tasks/{task.id}/tests/{test.id}")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_test_task_not_found(self, client):
        """Удаление теста из несуществующей задачи"""
        response = await client.delete("/api/tasks/999/tests/1")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_test_not_found(self, client, create_test_task):
        """Удаление несуществующего теста"""
        task = await create_test_task()

        response = await client.delete(f"/api/tasks/{task.id}/tests/999")

        assert response.status_code == 404


class TestPatchTaskTest:
    """Тесты PATCH /api/tasks/{task_id}/tests/{test_id}"""

    @pytest.mark.asyncio
    async def test_patch_test_success(self, client, create_test_task, create_test_test):
        """Успешное обновление теста"""
        task = await create_test_task()
        test = await create_test_test(task.id, title="Original", stdin="", stdout="old")

        response = await client.patch(
            f"/api/tasks/{task.id}/tests/{test.id}",
            json={"title": "Updated", "stdout": "new output"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"
        assert data["stdout"] == "new output"
        assert data["stdin"] == ""

    @pytest.mark.asyncio
    async def test_patch_test_task_not_found(self, client):
        """Обновление теста в несуществующей задаче"""
        response = await client.patch(
            "/api/tasks/999/tests/1", json={"title": "Updated"}
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_patch_test_not_found(self, client, create_test_task):
        """Обновление несуществующего теста"""
        task = await create_test_task()

        response = await client.patch(
            f"/api/tasks/{task.id}/tests/999", json={"title": "Updated"}
        )

        assert response.status_code == 404


class TestImportTests:
    """Тесты POST /api/tasks/{task_id}/tests/import"""

    @pytest.mark.asyncio
    async def test_import_tests_success(self, client, create_test_task):
        """Успешный импорт тестов из JSON"""
        task = await create_test_task()

        tests_data = {
            "tests": [
                {"title": "Test 1", "stdin": "", "stdout": "out1"},
                {"title": "Test 2", "stdin": "input", "stdout": "out2"},
                {"title": "Test 3", "stdin": "data", "stdout": "out3"},
            ]
        }

        files = {"file": ("tests.json", json.dumps(tests_data), "application/json")}

        response = await client.post(f"/api/tasks/{task.id}/tests/import", files=files)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["title"] == "Test 1"
        assert data[1]["title"] == "Test 2"
        assert data[2]["title"] == "Test 3"

    @pytest.mark.asyncio
    async def test_import_tests_invalid_json(self, client, create_test_task):
        """Импорт с невалидным JSON"""
        task = await create_test_task()

        files = {"file": ("tests.json", "invalid json {", "application/json")}

        response = await client.post(f"/api/tasks/{task.id}/tests/import", files=files)

        assert response.status_code == 400
        assert "Некорректный JSON" in response.json()["detail"]


class TestFullTaskFlow:
    """Полный цикл работы с задачами"""

    @pytest.mark.asyncio
    async def test_full_task_flow(self, client):

        create_response = await client.post(
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

        test1 = await client.post(
            f"/api/tasks/{task_id}/tests",
            json={"title": "Test 1", "stdin": "", "stdout": "output1"},
        )
        assert test1.status_code == 200
        test1_id = test1.json()["id"]

        test2 = await client.post(
            f"/api/tasks/{task_id}/tests",
            json={"title": "Test 2", "stdin": "input", "stdout": "output2"},
        )
        assert test2.status_code == 200
        get_tests = await client.get(f"/api/tasks/{task_id}/tests")
        assert len(get_tests.json()) == 2

        patch_test = await client.patch(
            f"/api/tasks/{task_id}/tests/{test1_id}",
            json={"title": "Updated Test", "stdout": "new_output"},
        )
        assert patch_test.status_code == 200
        assert patch_test.json()["title"] == "Updated Test"

        patch_task = await client.patch(
            f"/api/tasks/{task_id}", json={"title": "Updated Flow Task", "timeout": 60}
        )
        assert patch_task.status_code == 200
        assert patch_task.json()["title"] == "Updated Flow Task"

        delete_test = await client.delete(f"/api/tasks/{task_id}/tests/{test1_id}")
        assert delete_test.status_code == 204

        get_tests_after = await client.get(f"/api/tasks/{task_id}/tests")
        assert len(get_tests_after.json()) == 1

        delete_task = await client.delete(f"/api/tasks/{task_id}")
        assert delete_task.status_code == 204

        get_task = await client.get(f"/api/tasks/{task_id}")
        assert get_task.status_code == 404
