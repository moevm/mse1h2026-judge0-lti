import pytest

pytestmark = pytest.mark.integration
class TestGetModules:
    """Тесты GET /api/modules/"""

    @pytest.mark.asyncio
    async def test_get_modules_empty(self, client):
        """Получение списка модулей когда их нет"""
        response = await client.get("/api/modules/")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_modules_with_data(self, client, create_test_module):
        """Получение списка модулей с данными"""
        create_test_module(title="Module 1", description="Desc 1")
        create_test_module(title="Module 2", description="Desc 2")

        response = await client.get("/api/modules/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_modules_with_search(self, client, create_test_module):
        """Фильтрация модулей по поиску"""
        create_test_module(title="Python Basics", description="Learn Python")
        create_test_module(title="Java Basics", description="Learn Java")
        create_test_module(title="Advanced Python", description="Advanced topics")

        response = await client.get("/api/modules/?search=Python")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        titles = [m["title"] for m in data]
        assert "Python Basics" in titles
        assert "Advanced Python" in titles


class TestGetModule:
    """Тесты GET /api/modules/{module_id}"""

    @pytest.mark.asyncio
    async def test_get_module_success(self, client, create_test_module):
        """Получение модуля по ID"""
        module = create_test_module(title="Test Module", description="Test Desc")

        response = await client.get(f"/api/modules/{module.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == module.id
        assert data["title"] == "Test Module"
        assert data["description"] == "Test Desc"

    @pytest.mark.asyncio
    async def test_get_module_not_found(self, client):
        """Получение несуществующего модуля"""
        response = await client.get("/api/modules/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Модуль не найден"


class TestCreateModule:
    """Тесты POST /api/modules/"""

    @pytest.mark.asyncio
    async def test_create_module_success(self, client):
        """Успешное создание модуля"""
        response = await client.post(
            "/api/modules/",
            json={"title": "New Module", "description": "Module Description"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Module"
        assert data["description"] == "Module Description"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_module_empty_title(self, client):
        """Создание модуля с пустым заголовком"""
        response = await client.post(
            "/api/modules/", json={"title": "", "description": "Description"}
        )

        assert response.status_code == 422


class TestPatchModule:
    """Тесты PATCH /api/modules/{module_id}"""

    @pytest.mark.asyncio
    async def test_patch_module_success(self, client, create_test_module):
        """Успешное обновление модуля"""
        module = create_test_module(title="Original Title", description="Original Desc")

        response = await client.patch(
            f"/api/modules/{module.id}", json={"title": "Updated Title"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Original Desc"

    @pytest.mark.asyncio
    async def test_patch_module_not_found(self, client):
        """Обновление несуществующего модуля"""
        response = await client.patch(
            "/api/modules/999", json={"title": "Updated"}
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Модуль не найден"


class TestDeleteModule:
    """Тесты DELETE /api/modules/{module_id}"""

    @pytest.mark.asyncio
    async def test_delete_module_success(self, client, create_test_module):
        """Успешное удаление модуля"""
        module = create_test_module(title="To Delete")

        response = await client.delete(f"/api/modules/{module.id}")

        assert response.status_code == 204

        get_response = await client.get(f"/api/modules/{module.id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_module_not_found(self, client):
        """Удаление несуществующего модуля"""
        response = await client.delete("/api/modules/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Модуль не найден"


class TestGetModuleTasks:
    """Тесты GET /api/modules/{module_id}/tasks"""

    @pytest.mark.asyncio
    async def test_get_module_tasks_empty(self, client, create_test_module):
        """Получение задач пустого модуля"""
        module = create_test_module(title="Empty Module")

        response = await client.get(f"/api/modules/{module.id}/tasks")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_module_tasks_not_found(self, client):
        """Получение задач несуществующего модуля"""
        response = await client.get("/api/modules/999/tasks")
        assert response.status_code == 404
        assert response.json()["detail"] == "Модуль не найден"


class TestAddTasksToModule:
    """Тесты POST /api/modules/{module_id}/tasks"""

    @pytest.mark.asyncio
    async def test_add_tasks_success(
        self, client, create_test_module, create_test_tasks
    ):
        task1, task2, task3 = create_test_tasks(3)

        module = create_test_module(title="Module With Tasks")

        response = await client.post(
            f"/api/modules/{module.id}/tasks",
            json={"task_ids": [task1.id, task2.id, task3.id]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == module.id

    @pytest.mark.asyncio
    async def test_add_tasks_module_not_found(self, client):
        """Добавление задач в несуществующий модуль"""
        response = await client.post(
            "/api/modules/999/tasks", json={"task_ids": [1, 2]}
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Модуль не найден"

    @pytest.mark.asyncio
    async def test_add_tasks_with_duplicates(self, client, create_test_module):
        """Добавление дублирующихся задач в запросе"""
        module = create_test_module(title="Module")

        response = await client.post(
            f"/api/modules/{module.id}/tasks", json={"task_ids": [1, 1, 2, 2]}
        )

        assert response.status_code == 400
        assert "дублирующиеся" in response.json()["detail"]


class TestRemoveTaskFromModule:
    """Тесты DELETE /api/modules/{module_id}/tasks/{task_id}"""

    @pytest.mark.asyncio
    async def test_remove_task_success(
        self, client, create_test_module, create_test_tasks
    ):
        task1, task2, task3 = create_test_tasks(3)

        module = create_test_module(title="Module")

        await client.post(
            f"/api/modules/{module.id}/tasks",
            json={"task_ids": [task1.id, task2.id, task3.id]},
        )

        response = await client.delete(f"/api/modules/{module.id}/tasks/{task1.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == module.id
        task_ids = [ task['id'] for task in data["tasks"]]
        assert task1.id not in task_ids

    @pytest.mark.asyncio
    async def test_remove_task_module_not_found(self, client):
        """Удаление задачи из несуществующего модуля"""
        response = await client.delete("/api/modules/999/tasks/1")

        assert response.status_code == 404
        assert response.json()["detail"] == "Модуль не найден"


class TestReorderTasks:
    """Тесты PATCH /api/modules/{module_id}/tasks/reorder"""

    @pytest.mark.asyncio
    async def test_reorder_tasks_success(
        self, client, create_test_module, create_test_tasks
    ):
        task1, task2, task3 = create_test_tasks(3)

        module = create_test_module(title="Module")

        await client.post(
            f"/api/modules/{module.id}/tasks",
            json={"task_ids": [task1.id, task2.id, task3.id]},
        )

        response = await client.patch(
            f"/api/modules/{module.id}/tasks/reorder",
            json={
                "tasks": [
                    {"task_id": task3.id, "order": 1},
                    {"task_id": task1.id, "order": 2},
                    {"task_id": task2.id, "order": 3},
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == module.id

    @pytest.mark.asyncio
    async def test_reorder_tasks_module_not_found(self, client, create_test_tasks):
        """Изменение порядка в несуществующем модуле"""
        tasks = create_test_tasks(2)

        response = await client.patch(
            "/api/modules/999/tasks/reorder",
            json={
                "tasks": [
                    {"task_id": tasks[0].id, "order": 1},
                    {"task_id": tasks[1].id, "order": 2},
                ]
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Модуль не найден"

    @pytest.mark.asyncio
    async def test_reorder_tasks_with_duplicate_orders(
        self, client, create_test_module, create_test_tasks
    ):
        """Изменение порядка с дублирующимися order"""
        tasks = create_test_tasks(2)
        task1, task2 = tasks

        module = create_test_module(title="Module")

        await client.post(
            f"/api/modules/{module.id}/tasks", json={"task_ids": [task1.id, task2.id]}
        )

        response = await client.patch(
            f"/api/modules/{module.id}/tasks/reorder",
            json={
                "tasks": [
                    {"task_id": task1.id, "order": 1},
                    {"task_id": task2.id, "order": 1},
                ]
            },
        )

        assert response.status_code == 422


class TestFullModuleFlow:
    """Полный цикл работы с модулями"""

    @pytest.mark.asyncio
    async def test_full_module_flow(self, client, create_test_tasks):
        tasks = create_test_tasks(3)
        task1, task2, task3 = tasks

        create_response = await client.post(
            "/api/modules/", json={"title": "Flow Module", "description": "Test flow"}
        )
        assert create_response.status_code == 200
        module_id = create_response.json()["id"]

        add_response = await client.post(
            f"/api/modules/{module_id}/tasks",
            json={"task_ids": [task1.id, task2.id, task3.id]},
        )
        assert add_response.status_code == 200

        get_module = await client.get(f"/api/modules/{module_id}")
        assert get_module.status_code == 200

        reorder_response = await client.patch(
            f"/api/modules/{module_id}/tasks/reorder",
            json={
                "tasks": [
                    {"task_id": task3.id, "order": 1},
                    {"task_id": task1.id, "order": 2},
                    {"task_id": task2.id, "order": 3},
                ]
            },
        )
        assert reorder_response.status_code == 200

        remove_response = await client.delete(
            f"/api/modules/{module_id}/tasks/{task1.id}"
        )
        assert remove_response.status_code == 200

        delete_response = await client.delete(f"/api/modules/{module_id}")
        assert delete_response.status_code == 204

        get_response = await client.get(f"/api/modules/{module_id}")
        assert get_response.status_code == 404
