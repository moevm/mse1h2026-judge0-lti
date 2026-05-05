# tests/functional/test_run.py
import pytest


@pytest.mark.functional
class TestRunFunctional:
    """Функциональные тесты для /run эндпоинта"""

    @pytest.mark.asyncio
    async def test_run_simple_python_code(self, student_auth):
        """Запуск простого Python кода"""
        client, user = student_auth

        response = await client.post(
            "/api/run/",
            json={
                "source_code": 'print("Hello, World!")',
                "language": "Python (3.8.1)",
                "stdin": "",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "stdout" in data
        assert "Hello, World!" in data.get("stdout", "")
        assert data.get("stderr") is None or data.get("stderr") == ""

    @pytest.mark.asyncio
    async def test_run_python_code_with_input(self, student_auth):
        """Запуск Python кода с вводом данных"""
        client, user = student_auth

        code = """name = input()
print(f"Hello, {name}!")"""

        response = await client.post(
            "/api/run/",
            json={
                "source_code": code,
                "language": "Python (3.8.1)",
                "stdin": "Alice",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "Hello, Alice!" in data.get("stdout", "")

    @pytest.mark.asyncio
    async def test_run_python_code_with_error(self, student_auth):
        """Запуск кода с ошибкой"""
        client, user = student_auth

        response = await client.post(
            "/api/run/",
            json={
                "source_code": "raise ValueError('Test error')",
                "language": "Python (3.8.1)",
                "stdin": "",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("stderr") is not None
        assert "ValueError" in data.get("stderr", "")

    @pytest.mark.asyncio
    async def test_run_java_code(self, student_auth):
        """Запуск Java кода"""
        client, user = student_auth

        java_code = '''public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
    }
}'''

        response = await client.post(
            "/api/run/",
            json={
                "source_code": java_code,
                "language": "Java (OpenJDK 13.0.1)",
                "stdin": "",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "Hello from Java!" in data.get("stdout", "")

    @pytest.mark.asyncio
    async def test_run_javascript_code(self, student_auth):
        """Запуск JavaScript кода"""
        client, user = student_auth

        js_code = """console.log("Hello from JavaScript!");"""

        response = await client.post(
            "/api/run/",
            json={
                "source_code": js_code,
                "language": "JavaScript (Node.js 12.14.0)",
                "stdin": "",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "Hello from JavaScript!" in data.get("stdout", "")


    @pytest.mark.asyncio
    async def test_run_invalid_language(self, student_auth):
        """Запуск с невалидным языком программирования"""
        client, user = student_auth

        response = await client.post(
            "/api/run/",
            json={
                "source_code": 'print("test")',
                "language": "invalid_language",
                "stdin": "",
            },
        )

        assert response.status_code == 400
        assert "Недопустимый язык программирования" in response.json()["detail"]


@pytest.mark.functional
class TestRunFullFlow:
    """Полный цикл работы с запуском кода"""

    @pytest.mark.asyncio
    async def test_full_run_flow(self, student_auth):
        client, user = student_auth

        response = await client.post(
            "/api/run/",
            json={
                "source_code": 'print("Python")',
                "language": "Python (3.8.1)",
                "stdin": "",
            },
        )
        assert response.status_code == 200
        assert "Python" in response.json().get("stdout", "")

        response = await client.post(
            "/api/run/",
            json={
                "source_code": 'console.log("JavaScript")',
                "language": "JavaScript (Node.js 12.14.0)",
                "stdin": "",
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
                "source_code": java_code,
                "language": "Java (OpenJDK 13.0.1)",
                "stdin": "",
            },
        )
        assert response.status_code == 200
        assert "Java" in response.json().get("stdout", "")