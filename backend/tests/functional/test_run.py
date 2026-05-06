import pytest
from datetime import datetime, timezone

@pytest.mark.functional
class TestRunFunctional:
    """Функциональные тесты для /run эндпоинта"""

    @pytest.mark.asyncio
    async def test_run_simple_python_code(self, admin_auth):
        """Запуск простого Python кода"""
        client = admin_auth

        response = await client.post(
            "/api/run/",
            json={
                "code": 'print("Hello, World!")',
                "language": "Python (3.8.1)",
                "stdin": "",
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "stdout" in data
        assert "Hello, World!" in data.get("stdout", "")
        assert data.get("stderr") is None or data.get("stderr") == ""

    @pytest.mark.asyncio
    async def test_run_python_code_with_input(self, admin_auth):
        """Запуск Python кода с вводом данных"""
        client = admin_auth

        code = """print(f"Hello, {input()}!")"""

        response = await client.post(
            "/api/run/",
            json={
                "code": code,
                "language": "Python (3.8.1)",
                "stdin": "Alice",
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "Hello, Alice!" in data.get("stdout", "")

    @pytest.mark.asyncio
    async def test_run_python_code_with_error(self,admin_auth):
        """Запуск кода с ошибкой"""
        client = admin_auth

        response = await client.post(
            "/api/run/",
            json={
                "code": "raise ValueError('Test error')",
                "language": "Python (3.8.1)",
                "stdin": "",
                 "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("stderr") is not None
        assert "ValueError" in data.get("stderr", "")

    @pytest.mark.asyncio
    async def test_run_java_code(self, admin_auth):
        """Запуск Java кода"""
        client = admin_auth

        java_code = '''public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
    }
}'''

        response = await client.post(
            "/api/run/",
            json={
                "code": java_code,
                "language": "Java (OpenJDK 13.0.1)",
                "stdin": "",
                 "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "Hello from Java!" in data.get("stdout", "")

    @pytest.mark.asyncio
    async def test_run_javascript_code(self, admin_auth):
        """Запуск JavaScript кода"""
        client = admin_auth

        js_code = """console.log("Hello from JavaScript!");"""

        response = await client.post(
            "/api/run/",
            json={
                "code": js_code,
                "language": "JavaScript (Node.js 12.14.0)",
                "stdin": "",
                 "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "Hello from JavaScript!" in data.get("stdout", "")


    @pytest.mark.asyncio
    async def test_run_invalid_language(self, admin_auth):
        """Запуск с невалидным языком программирования"""
        client = admin_auth

        response = await client.post(
            "/api/run/",
            json={
                "code": 'print("test")',
                "language": "invalid_language",
                "stdin": "",
                 "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 400
        assert "Недопустимый язык программирования" in response.json()["detail"]


@pytest.mark.functional
class TestRunFullFlow:
    """Полный цикл работы с запуском кода"""

    @pytest.mark.asyncio
    async def test_full_run_flow(self, admin_auth):
        client = admin_auth

        response = await client.post(
            "/api/run/",
            json={
                "code": 'print("Python")',
                "language": "Python (3.8.1)",
                "stdin": "",
                 "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert response.status_code == 200
        assert "Python" in response.json().get("stdout", "")

        response = await client.post(
            "/api/run/",
            json={
                "code": 'console.log("JavaScript")',
                "language": "JavaScript (Node.js 12.14.0)",
                "stdin": "",
                 "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert response.status_code == 200
        assert "JavaScript" in response.json().get("stdout", "")

        java_code = '''public class Main {
    public static void main(String[] args) {
        System.out.println("Java");
    }
}'''
        response = await client.post(
            "/api/run/",
            json={
                "code": java_code,
                "language": "Java (OpenJDK 13.0.1)",
                "stdin": "",
                 "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert response.status_code == 200
        assert "Java" in response.json().get("stdout", "")