from typing import List
from fastapi.params import Depends
from app.repositories.task import TaskRepository, get_task_repository
from app.database.models import Task
from app.schemas.task import TaskPatch, TaskCreate, TaskTest
from app.repositories.language import LanguageRepository, get_language_repository


class TaskNotFoundException(Exception):
    pass


class InvalidLanguageException(Exception):
    pass


class TaskService:
    def __init__(self, repo: TaskRepository, lang_repo: LanguageRepository) -> None:
        self.repo = repo
        self.lang_repo = lang_repo

    def get_task_by_id(self, task_id: int) -> Task:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException
        return task

    def get_all_tasks(self) -> List[Task]:
        tasks = self.repo.get_all()
        return tasks

    def create_task(self, body: TaskCreate) -> Task:
        data = body.model_dump()
        lang_names = data.pop("languages")
        languages = self._resolve_languages(lang_names)
        task = Task(**data)
        task.languages = languages
        self.repo.add(task)
        return self.repo.save(task)

    def update_task(self, task_id: int, data: TaskPatch) -> Task:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException
        update_data = data.model_dump(exclude_unset=True)
        if "languages" in update_data:
            lang_names = update_data.pop("languages")
            task.languages = self._resolve_languages(lang_names)
        for key, value in update_data.items():
            setattr(task, key, value)
        return self.repo.save(task)

    def _resolve_languages(self, lang_names: List[str]):
        languages = self.lang_repo.get_by_names(lang_names)
        found = {l.language for l in languages}
        requested = set(lang_names)
        if found != requested:
            raise InvalidLanguageException
        return languages

    def delete_task(self, task_id: int) -> None:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException
        self.repo.delete(task)

    def get_task_tests(self, task_id: int) -> List[dict]:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException
        return task.tests_pipeline

    def create_task_test(self, task_id, body: TaskTest):
        task = self.repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException
        tests = task.tests_pipeline or []
        tests.append(body.model_dump())
        task.tests_pipeline = tests
        return self.repo.save(task)


def get_task_service(
    repo: TaskRepository = Depends(get_task_repository),
    lang_repo: LanguageRepository = Depends(get_language_repository),
) -> TaskService:
    return TaskService(repo, lang_repo)
