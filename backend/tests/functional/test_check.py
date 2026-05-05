import pytest
from datetime import datetime, timezone


@pytest.mark.functional
class TestCheckFunctional:
    """Функциональные тесты для /check"""

    @pytest.mark.asyncio
    async def test_check_correct_python_code(self, admin_auth, create_task_via_api):
        client = admin_auth

        task = await create_task_via_api(
            title="Sum of two numbers",
            description="Calculate sum of two integers",
            timeout=30,
            languages=["Python (3.8.1)"],
        )

        test_cases = [
            {"title": "Test 1", "stdin": "2 3", "stdout": "5"},
            {"title": "Test 2", "stdin": "10 20", "stdout": "30"},
            {"title": "Test 3", "stdin": "-1 5", "stdout": "4"},
        ]
        for tc in test_cases:
            response = await client.post(
                f"/api/tasks/{task['id']}/tests",
                json={
                    "title": tc["title"],
                    "stdin": tc["stdin"],
                    "stdout": tc["stdout"],
                },
            )
            assert response.status_code == 200

        correct_code = """print(sum(map(int, input().split())))"""

        response = await client.post(
            f"/api/check/{task['id']}",
            json={
                "language": "Python (3.8.1)",
                "code": correct_code,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_check_incorrect_python_code(
        self, admin_auth, create_task_via_api
    ):
        """Проверка неправильного Python кода"""
        client = admin_auth

        task = await create_task_via_api(
            title="Sum of two numbers",
            description="Calculate sum of two integers",
            timeout=30,
            languages=["Python (3.8.1)"],
        )

        test_cases = [
            {"title": "Test 1", "stdin": "2 3", "stdout": "5"},
            {"title": "Test 2", "stdin": "10 20", "stdout": "30"},
        ]
        for tc in test_cases:
            response = await client.post(
                f"/api/tasks/{task['id']}/tests",
                json={"title": tc["title"], "stdin": tc["stdin"], "stdout": tc["stdout"]},
            )
            assert response.status_code == 200

        # Проверяем неправильное решение
        incorrect_code = """print(sum(map(int, input().split())) + 1)"""

        response = await client.post(
            f"/api/check/{task['id']}",
            json={
                "language": "Python (3.8.1)",
                "code": incorrect_code,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_check_python_code_with_compilation_error(
        self, admin_auth, create_task_via_api
    ):
        """Проверка Python кода с синтаксической ошибкой"""
        client = admin_auth

        task = await create_task_via_api(
            title="Simple task",
            description="Print Hello",
            timeout=30,
            languages=["Python (3.8.1)"],
        )

        response = await client.post(
            f"/api/tasks/{task['id']}/tests",
            json={"title": "Test", "stdin": "", "stdout": "Hello"},
        )
        assert response.status_code == 200

        code_with_error = """print("Hello"""

        response = await client.post(
            f"/api/check/{task['id']}",
            json={
                "language": "Python (3.8.1)",
                "code": code_with_error,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_check_task_not_found(self, admin_auth):
        """Проверка несуществующей задачи"""
        client = admin_auth

        response = await client.post(
            "/api/check/99999",
            json={
                "language": "Python (3.8.1)",
                "code": 'print("test")',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 404
        assert "не найдена" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_check_invalid_language(self, admin_auth, create_task_via_api):
        """Проверка с невалидным языком программирования"""
        client = admin_auth

        task = await create_task_via_api(
            title="Test task",
            description="Test",
            timeout=30,
            languages=["Python (3.8.1)"],
        )

        # Пытаемся проверить решение на java
        response = await client.post(
            f"/api/check/{task['id']}",
            json={
                "language": "Java (OpenJDK 13.0.1)",
                "code": 'public class Main { public static void main(String[] args) {} }',
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 400
        assert "недопустимый язык" in response.json()["detail"].lower()


@pytest.mark.functional
class TestCheckWithMultipleLanguages:
    """Тесты /check с разными языками программирования"""

    @pytest.mark.asyncio
    async def test_check_java_code(
        self, admin_auth, create_task_via_api
    ):
        """Проверка Java кода"""
        client = admin_auth

        task = await create_task_via_api(
            title="Java Sum",
            description="Sum of two numbers in Java",
            timeout=30,
            languages=["Java (OpenJDK 13.0.1)"],
        )

        response = await client.post(
            f"/api/tasks/{task['id']}/tests",
            json={"title": "Test", "stdin": "2 3", "stdout": "5"},
        )
        assert response.status_code == 200

        java_code = '''import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.println(a + b);
    }
}'''

        response = await client.post(
            f"/api/check/{task['id']}",
            json={
                "language": "Java (OpenJDK 13.0.1)",
                "code": java_code,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_check_javascript_code(
        self, admin_auth, create_task_via_api
    ):
        """Проверка JavaScript кода"""
        client = admin_auth

        task = await create_task_via_api(
            title="JS Sum",
            description="Sum of two numbers in JavaScript",
            timeout=30,
            languages=["JavaScript (Node.js 12.14.0)"],
        )

        response = await client.post(
            f"/api/tasks/{task['id']}/tests",
            json={"title": "Test", "stdin": "2 3", "stdout": "5"},
        )
        assert response.status_code == 200

        js_code = """const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});
rl.on('line', (input) => {
    const [a, b] = input.split(' ').map(Number);
    console.log(a + b);
});"""

        response = await client.post(
            f"/api/check/{task['id']}",
            json={
                "language": "JavaScript (Node.js 12.14.0)",
                "code": js_code,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


@pytest.mark.functional
class TestCheckFullFlow:
    """Полный цикл работы с проверкой решений"""

    @pytest.mark.asyncio
    async def test_full_check_flow(
        self, admin_auth, create_task_via_api
    ):
        client = admin_auth

        task = await create_task_via_api(
            title="FizzBuzz",
            description="Classic FizzBuzz problem",
            timeout=30,
            languages=["python"],
        )

        test_cases = [
            {"title": "Test 1", "stdin": "3", "stdout": "Fizz"},
            {"title": "Test 2", "stdin": "5", "stdout": "Buzz"},
            {"title": "Test 3", "stdin": "15", "stdout": "FizzBuzz"},
            {"title": "Test 4", "stdin": "2", "stdout": "2"},
        ]
        for tc in test_cases:
            response = await client.post(
                f"/api/tasks/{task['id']}/tests",
                json={"title": tc["title"], "stdin": tc["stdin"], "stdout": tc["stdout"]},
            )
            assert response.status_code == 200

        wrong_code = """n = int(input())
if n % 3 == 0:
    print("Fizz")
elif n % 5 == 0:
    print("Buzz")
else:
    print(n)"""

        wrong_response = await client.post(
            f"/api/check/{task['id']}",
            json={
                "language": "Python (3.8.1)",
                "code": wrong_code,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert wrong_response.status_code == 200
        assert wrong_response.json()["success"] is False

        correct_code = """n = int(input())
if n % 3 == 0 and n % 5 == 0:
    print("FizzBuzz")
elif n % 3 == 0:
    print("Fizz")
elif n % 5 == 0:
    print("Buzz")
else:
    print(n)"""

        correct_response = await client.post(
            f"/api/check/{task['id']}",
            json={
                "language": "Python (3.8.1)",
                "code": correct_code,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert correct_response.status_code == 200
        assert correct_response.json()["success"] is True
