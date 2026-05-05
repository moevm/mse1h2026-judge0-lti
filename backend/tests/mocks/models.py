from datetime import datetime, timezone

class MockUser:
    def __init__(
        self,
        username: str,
        password_hash: str,
        full_name: str = "Test User",
        role: str = "student",
    ):
        self.id = None
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name
        self.role = type("Role", (), {"value": role})()
        self.deleted_at = None


class MockRefreshToken:
    def __init__(self, user_id: int, token_hash: str, expires_at):
        self.id = None
        self.user_id = user_id
        self.token_hash = token_hash
        self.expires_at = expires_at
        self.revoked = False


class MockTask:
    def __init__(self, title: str, description: str, timeout: int, languages: list):
        self.id = None
        self.title = title
        self.description = description
        self.timeout = timeout
        self.languages = languages
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.tests = []


class MockTaskTest:
    def __init__(self, title: str, stdin: str, stdout: str, task_id: int = None):
        self.id = None
        self.title = title
        self.stdin = stdin
        self.stdout = stdout
        self.task_id = task_id


class MockLanguage:
    def __init__(self, id: int, language: str):
        self.id = id
        self.language = language
        self.created_at = None
