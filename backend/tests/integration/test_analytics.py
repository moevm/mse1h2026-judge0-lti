import pytest
from datetime import datetime, timedelta, timezone

pytestmark = pytest.mark.integration
class TestUserModules:
    """Тесты GET /users/{user_id}/modules"""

    @pytest.mark.asyncio
    async def test_get_user_modules_success(
        self, auth_client, create_test_module, create_test_task
    ):
        """Успешное получение модулей пользователя"""
        client, user = auth_client
        module = create_test_module(title="Python Basics", description="Learn Python")
        task = create_test_task(title="Task 1")

        await client.post(
            f"/api/modules/{module.id}/tasks", json={"task_ids": [task.id]}
        )

        check_response = await client.post(
            f"/api/check/{task.id}",
            json={
                "language": "python",
                "code": 'print("Hello, World!")',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert check_response.status_code == 200

        response = await client.get(f"/api/users/{user.id}/modules")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["title"] == "Python Basics"
        assert data[0]["task_count"] == 1
        assert "created_at" in data[0]

    @pytest.mark.asyncio
    async def test_get_user_modules_with_search(
        self, auth_client, create_test_module, create_test_task
    ):
        """Фильтрация модулей по поиску"""
        client, user = auth_client

        module1 = create_test_module(title="Python Basics", description="Learn Python")
        task1 = create_test_task(title="Python Task")
        await client.post(
            f"/api/modules/{module1.id}/tasks", json={"task_ids": [task1.id]}
        )
        await client.post(
            f"/api/check/{task1.id}",
            json={
                "language": "python",
                "code": 'print("Python")',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        module2 = create_test_module(title="Java Basics", description="Learn Java")
        task2 = create_test_task(title="Java Task")
        await client.post(
            f"/api/modules/{module2.id}/tasks", json={"task_ids": [task2.id]}
        )
        await client.post(
            f"/api/check/{task2.id}",
            json={
                "language": "java",
                "code": 'System.out.println("Java");',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        response = await client.get(f"/api/users/{user.id}/modules?search=Python")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Python" in data[0]["title"]

    @pytest.mark.asyncio
    async def test_get_user_modules_sorted_by_tasks_count(
        self, auth_client, create_test_module, create_test_task
    ):
        """Сортировка модулей по количеству задач"""
        client, user = auth_client

        module1 = create_test_module(title="Module 1")
        task1 = create_test_task(title="Task 1")
        await client.post(
            f"/api/modules/{module1.id}/tasks", json={"task_ids": [task1.id]}
        )
        await client.post(
            f"/api/check/{task1.id}",
            json={
                "language": "python",
                "code": 'print("task1")',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        module2 = create_test_module(title="Module 2")
        task2 = create_test_task(title="Task 2")
        task3 = create_test_task(title="Task 3")
        await client.post(
            f"/api/modules/{module2.id}/tasks", json={"task_ids": [task2.id, task3.id]}
        )
        await client.post(
            f"/api/check/{task2.id}",
            json={
                "language": "python",
                "code": 'print("task2")',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        await client.post(
            f"/api/check/{task3.id}",
            json={
                "language": "python",
                "code": 'print("task3")',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        response = await client.get(
            f"/api/users/{user.id}/modules?sort_by=tasks_count&sort_order=desc"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["task_count"] == 2
        assert data[1]["task_count"] == 1

    @pytest.mark.asyncio
    async def test_get_user_modules_empty(self, auth_client):
        """Пользователь без решенных задач - нет модулей"""
        client, user = auth_client

        response = await client.get(f"/api/users/{user.id}/modules")

        assert response.status_code == 200
        assert response.json() == []


class TestUserTasksInModule:
    """Тесты GET /users/{user_id}/modules/{module_id}/tasks"""

    @pytest.mark.asyncio
    async def test_get_user_tasks_success(
        self, auth_client, create_test_module, create_test_task
    ):
        """Успешное получение задач модуля"""
        client, user = auth_client
        module = create_test_module(title="Module")
        task1 = create_test_task(title="Task 1")
        task2 = create_test_task(title="Task 2")

        await client.post(
            f"/api/modules/{module.id}/tasks", json={"task_ids": [task1.id, task2.id]}
        )

        await client.post(
            f"/api/check/{task1.id}",
            json={
                "language": "python",
                "code": 'print("task1")',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        await client.post(
            f"/api/check/{task2.id}",
            json={
                "language": "python",
                "code": 'print("task2")',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        response = await client.get(f"/api/users/{user.id}/modules/{module.id}/tasks")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        titles = [t["title"] for t in data]
        assert "Task 1" in titles
        assert "Task 2" in titles

    @pytest.mark.asyncio
    async def test_get_user_tasks_with_solution(
        self, auth_client, create_test_module, create_test_task
    ):
        """Получение задач модуля с решениями"""
        client, user = auth_client
        module = create_test_module(title="Module")
        task = create_test_task(title="Task to Solve")

        await client.post(
            f"/api/modules/{module.id}/tasks", json={"task_ids": [task.id]}
        )

        response = await client.post(
            f"/api/check/{task.id}",
            json={
                "language": "python",
                "code": 'print("Hello, World!")',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 200
        tasks_response = await client.get(
            f"/api/users/{user.id}/modules/{module.id}/tasks"
        )

        assert tasks_response.status_code == 200
        data = tasks_response.json()
        task_data = next((t for t in data if t["id"] == task.id), None)
        assert task_data is not None
        assert task_data["is_solved"] is True
        assert task_data["attempt_count"] >= 1

    @pytest.mark.asyncio
    async def test_get_user_tasks_with_attempt_count_filter(
        self, auth_client, create_test_module, create_test_task
    ):
        """Фильтрация по количеству попыток"""
        client, user = auth_client
        module = create_test_module()
        task = create_test_task()

        await client.post(
            f"/api/modules/{module.id}/tasks", json={"task_ids": [task.id]}
        )

        for i in range(3):
            await client.post(
                f"/api/check/{task.id}",
                json={
                    "language": "python",
                    "code": f'print("attempt {i+1}")',
                    "submitted_at": datetime.now(timezone.utc).isoformat(),
                },
            )

        response = await client.get(
            f"/api/users/{user.id}/modules/{module.id}/tasks?attempt_count_min=2"
        )

        assert response.status_code == 200
        data = response.json()
        task_data = next((t for t in data if t["id"] == task.id), None)
        assert task_data is not None
        assert task_data["attempt_count"] >= 2

    @pytest.mark.asyncio
    async def test_get_user_tasks_with_search(
        self, auth_client, create_test_module, create_test_task
    ):
        """Фильтрация задач по поиску"""
        client, user = auth_client
        module = create_test_module()
        task1 = create_test_task(title="Python Task")
        task2 = create_test_task(title="Java Task")

        await client.post(
            f"/api/modules/{module.id}/tasks", json={"task_ids": [task1.id, task2.id]}
        )

        await client.post(
            f"/api/check/{task1.id}",
            json={
                "language": "python",
                "code": 'print("python")',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        await client.post(
            f"/api/check/{task2.id}",
            json={
                "language": "java",
                "code": 'System.out.println("java");',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        response = await client.get(
            f"/api/users/{user.id}/modules/{module.id}/tasks?search=Python"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Python" in data[0]["title"]

    @pytest.mark.asyncio
    async def test_get_user_tasks_empty_module(self, auth_client, create_test_module):
        """Модуль без задач"""
        client, user = auth_client
        module = create_test_module(title="Empty Module")

        response = await client.get(f"/api/users/{user.id}/modules/{module.id}/tasks")

        assert response.status_code == 200
        assert response.json() == []


class TestTaskAttempts:
    """Тесты GET /tasks/{task_id}/attempts"""

    @pytest.mark.asyncio
    async def test_get_task_attempts_success(self, auth_client, create_test_task):
        """Успешное получение попыток задачи"""
        client, user = auth_client
        task = create_test_task()

        for i in range(3):
            await client.post(
                f"/api/check/{task.id}",
                json={
                    "language": "python",
                    "code": f'print("attempt {i+1}")',
                    "submitted_at": datetime.now(timezone.utc).isoformat(),
                },
            )

        response = await client.get(f"/api/tasks/{task.id}/attempts?user_id={user.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert "source_code" in data[0]
        assert "created_at" in data[0]
        assert "is_solved" in data[0]
        assert "language" in data[0]


    @pytest.mark.asyncio
    async def test_get_task_attempts_with_date_range(
        self, auth_client, create_test_task
    ):
        """Фильтрация попыток по диапазону дат"""
        client, user = auth_client
        task = create_test_task()

        await client.post(
            f"/api/check/{task.id}",
            json={
                "language": "python",
                "code": 'print("test")',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        from_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        to_date = (datetime.now(timezone.utc) + timedelta(days=1)).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )

        response = await client.get(
            f"/api/tasks/{task.id}/attempts?user_id={user.id}&from_date={from_date}&to_date={to_date}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    @pytest.mark.asyncio
    async def test_get_task_attempts_language_filter(
        self, auth_client, create_test_task
    ):
        """Фильтрация попыток по языку программирования"""
        client, user = auth_client
        task = create_test_task()

        await client.post(
            f"/api/check/{task.id}",
            json={
                "language": "python",
                "code": 'print("python code")',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        response = await client.get(
            f"/api/tasks/{task.id}/attempts?user_id={user.id}&language=python"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["language"] == "python"


class TestGetAttempt:
    """Тесты GET /attempts/{attempt_id}"""

    @pytest.mark.asyncio
    async def test_get_attempt_success(self, auth_client, create_test_task):
        """Успешное получение попытки по ID"""
        client, user = auth_client
        task = create_test_task()

        check_response = await client.post(
            f"/api/check/{task.id}",
            json={
                "language": "python",
                "code": 'print("Hello, World!")',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert check_response.status_code == 200
        attempt_id = check_response.json().get("attempt_id")

        if not attempt_id:
            attempts_response = await client.get(
                f"/api/tasks/{task.id}/attempts?user_id={user.id}"
            )
            attempt_id = attempts_response.json()[0]["id"]

        response = await client.get(f"/api/attempts/{attempt_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == attempt_id
        assert "source_code" in data
        assert data["source_code"] == 'print("Hello, World!")'
        assert "created_at" in data
        assert "language" in data

    @pytest.mark.asyncio
    async def test_get_attempt_not_found(self, auth_client):
        """Попытка не найдена"""
        client, _ = auth_client
        response = await client.get("/api/attempts/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Попытка не найдена"


class TestFullAnalyticsFlow:
    """Полный цикл работы с аналитикой"""

    @pytest.mark.asyncio
    async def test_full_analytics_flow(
        self, auth_client, create_test_module, create_test_task
    ):

        client, user = auth_client

        module = create_test_module(title="Analytics Module", description="Test")
        task = create_test_task(title="Analytics Task")

        await client.post(
            f"/api/modules/{module.id}/tasks", json={"task_ids": [task.id]}
        )

        check_response = await client.post(
            f"/api/check/{task.id}",
            json={
                "language": "python",
                "code": 'print("Hello, Analytics!")',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert check_response.status_code == 200
        assert check_response.json()["success"] is True

        modules_response = await client.get(f"/api/users/{user.id}/modules")
        assert modules_response.status_code == 200
        modules_data = modules_response.json()

        target_module = next(
            (m for m in modules_data if m["title"] == "Analytics Module"), None
        )
        assert target_module is not None
        assert target_module["task_count"] == 1

        tasks_response = await client.get(
            f"/api/users/{user.id}/modules/{module.id}/tasks"
        )
        assert tasks_response.status_code == 200
        tasks_data = tasks_response.json()

        target_task = next(
            (t for t in tasks_data if t["title"] == "Analytics Task"), None
        )
        assert target_task is not None
        assert target_task["is_solved"] is True
        assert target_task["attempt_count"] >= 1

        attempts_response = await client.get(
            f"/api/tasks/{task.id}/attempts?user_id={user.id}"
        )
        assert attempts_response.status_code == 200
        attempts_data = attempts_response.json()
        assert len(attempts_data) >= 1
        assert attempts_data[0]["source_code"] == 'print("Hello, Analytics!")'
