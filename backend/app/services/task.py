from typing import List
from fastapi.params import Depends
from app.repositories.task import TaskRepository, get_task_repository
from app.database.models import Task, TaskTest
from app.schemas.task import TaskPatch, TaskCreate, TaskFilter
from app.repositories.language import LanguageRepository, get_language_repository
from app.core.exceptions.tasks import InvalidLanguageException, TaskNotFoundException


class TaskService:
    def __init__(self, repo: TaskRepository, lang_repo: LanguageRepository) -> None:
        self.repo = repo
        self.lang_repo = lang_repo

    def get_task_by_id(self, task_id: int) -> Task:
        task = self._get_task_or_raise(task_id)
        return task

    def get_all_tasks(self) -> List[Task]:
        tasks = self.repo.get_all()
        return tasks

    def create_task(self, body: TaskCreate) -> Task:
        data = body.model_dump()
        lang_names = data.pop("languages")
        languages = self._resolve_languages(lang_names)
        task = Task(
            title=body.title,
            description=body.description,
            timeout=body.timeout,
            max_attempts=body.max_attempts,
        )
        task.languages = languages
        if body.tests:
            task.tests = [
                TaskTest(
                    title=test.title,
                    stdin=test.stdin,
                    stdout=test.stdout,
                )
                for test in body.tests
            ]
        self.repo.add(task)
        return self.repo.save(task)

    def update_task(self, task_id: int, data: TaskPatch) -> Task:
        task = self._get_task_or_raise(task_id)
        update_data = data.model_dump(exclude_unset=True)
        if "languages" in update_data:
            lang_names = update_data.pop("languages")
            task.languages = self._resolve_languages(lang_names)
        if "tests" in update_data:
            tests_data = update_data.pop("tests")
            task.tests = [
                TaskTest(
                    title=t["title"],
                    stdin=t.get("stdin", ""),
                    stdout=t["stdout"],
                )
                for t in tests_data
            ]
        for key, value in update_data.items():
            setattr(task, key, value)
        return self.repo.save(task)

    def _resolve_languages(self, lang_names: List[str]):
        languages = self.lang_repo.get_by_names(lang_names)
        found = {l.language for l in languages}
        requested = set(lang_names)
        if found != requested:
            raise InvalidLanguageException()
        return languages

    def get_filtered_tasks(self, filters: TaskFilter):
        return self.repo.get_filtered(filters)

    def delete_task(self, task_id: int) -> None:
        task = self._get_task_or_raise(task_id)
        self.repo.delete(task)

    def _get_task_or_raise(self, task_id: int) -> Task:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException(f"Задача {task_id} не найдена")
        return task


def get_task_service(
    repo: TaskRepository = Depends(get_task_repository),
    lang_repo: LanguageRepository = Depends(get_language_repository),
) -> TaskService:
    return TaskService(repo, lang_repo)
