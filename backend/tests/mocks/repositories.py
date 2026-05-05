from datetime import datetime, timezone

from app.repositories.user import UserRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.language import LanguageRepository
from app.repositories.task import TaskRepository
from app.repositories.task_test import TaskTestRepository
from app.database.models import Language


class MockUserRepository(UserRepository):
    """Мок репозитория юзеров"""
    def __init__(self):
        self.users = {}
        self.next_id = 1

    def get_by_id(self, user_id: int):
        return self.users.get(user_id)

    def get_by_username(self, username: str):
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def add(self, user):
        user.id = self.next_id
        self.users[self.next_id] = user
        self.next_id += 1

    def get_all(self, filters=None):
        return list(self.users.values())

    def get_solved_count(self, user_id: int):
        return 0

    def clear(self):
        self.users.clear()
        self.next_id = 1


class MockRefreshTokenRepository(RefreshTokenRepository):
    """Мок репозитория refresh токенов"""
    def __init__(self):
        self.tokens = {}
        self.next_id = 1

    def add(self, token):
        token.id = self.next_id
        self.tokens[self.next_id] = token
        self.next_id += 1

    def get_by_hash(self, token_hash: str):
        for token in self.tokens.values():
            if token.token_hash == token_hash:
                return token
        return None

    def delete_all_by_user(self, user_id: int):
        to_delete = [tid for tid, t in self.tokens.items() if t.user_id == user_id]
        for tid in to_delete:
            del self.tokens[tid]

    def revoke(self, token):
        token.revoked = True

    def clear(self):
        self.tokens.clear()
        self.next_id = 1


class MockTaskRepository(TaskRepository):
    """Мок репозитория задач"""
    def __init__(self):
        self.tasks = {}
        self.next_id = 1
        self.test_id_counter = 100

    def get_all(self):
        return list(self.tasks.values())

    def get_by_id(self, task_id: int):
        return self.tasks.get(task_id)

    def add(self, task):
        task.id = self.next_id
        task.created_at = datetime.now(timezone.utc)
        task.updated_at = datetime.now(timezone.utc)
        if hasattr(task, "tests"):
            for test in task.tests:
                if test.id is None:
                    test.id = self.test_id_counter
                    self.test_id_counter += 1
        self.tasks[self.next_id] = task
        self.next_id += 1

    def delete(self, task):
        if task.id in self.tasks:
            del self.tasks[task.id]

    def get_filtered(self, filters):
        tasks = list(self.tasks.values())

        if filters.search:
            search = filters.search.lower()
            tasks = [
                t
                for t in tasks
                if search in t.title.lower() or search in (t.description or "").lower()
            ]

        if filters.timeout_from is not None:
            tasks = [t for t in tasks if t.timeout >= filters.timeout_from]

        if filters.timeout_to is not None:
            tasks = [t for t in tasks if t.timeout <= filters.timeout_to]

        return tasks

    def save(self, task):
        return task

    def clear(self):
        self.tasks.clear()
        self.next_id = 1


class MockTaskTestRepository(TaskTestRepository):
    """Мок репозитория тестов задач"""
    def __init__(self):
        self.tests = {}
        self.next_id = 1

    def get_by_task_id(self, task_id: int):
        return [t for t in self.tests.values() if t.task_id == task_id]

    def get_by_id(self, test_id: int):
        return self.tests.get(test_id)

    def add(self, test):
        test.id = self.next_id
        self.tests[self.next_id] = test
        self.next_id += 1
        return test

    def add_all(self, tests):
        for test in tests:
            self.add(test)

    def delete(self, test):
        if test.id in self.tests:
            del self.tests[test.id]

    def save(self, test):
        return test

    def flush(self):
        pass

    def clear(self):
        self.tests.clear()
        self.next_id = 1


class MockLanguageRepository(LanguageRepository):
    """Мок репозитория языков"""
    def __init__(self):
        self._languages = {}
        self._next_id = 1

        for lang_name in ["python", "javascript", "java", "cpp"]:
            lang = Language()
            lang.id = self._next_id
            lang.language = lang_name
            self._languages[lang_name] = lang
            self._next_id += 1

    def get_all(self):
        return list(self._languages.values())

    def get_language_by_name(self, language_name: str):
        return self._languages.get(language_name)

    def get_by_names(self, names: list[str]):
        result = []
        for name in names:
            lang = self.get_language_by_name(name)
            if lang:
                result.append(lang)
        return result

    def add_language(self, name: str):
        if name not in self._languages:
            lang = Language()
            lang.id = self._next_id
            lang.language = name
            self._languages[name] = lang
            self._next_id += 1

    def clear(self):
        self._languages = {}
        self._next_id = 1
        for lang_name in ["python", "javascript", "java", "cpp"]:
            lang = Language()
            lang.id = self._next_id
            lang.language = lang_name
            self._languages[lang_name] = lang
            self._next_id += 1
