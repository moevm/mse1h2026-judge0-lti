from typing import List
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import session_generator
from app.repositories.task import TaskRepository, get_task_repository
from app.database.models import Task, TaskTest
from app.schemas.task import TaskPatch, TaskCreate, TaskFilter
from app.repositories.language import LanguageRepository, get_language_repository
from app.core.exceptions.tasks import InvalidLanguageException, TaskNotFoundException


class TaskService:
    def __init__(self, db: AsyncSession, repo: TaskRepository, lang_repo: LanguageRepository) -> None:
        self.db = db
        self.repo = repo
        self.lang_repo = lang_repo

    async def get_task_by_id(self, task_id: int) -> Task:
        return await self._get_task_or_raise(task_id)

    async def get_all_tasks(self) -> List[Task]:
        return await self.repo.get_all()

    async def create_task(self, body: TaskCreate) -> Task:
        data = body.model_dump()
        lang_names = data.pop("languages")
        languages = await self._resolve_languages(lang_names)
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
        await self.repo.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task
    async def update_task(self, task_id: int, data: TaskPatch) -> Task:
        task = await self._get_task_or_raise(task_id)
        update_data = data.model_dump(exclude_unset=True)
        if "languages" in update_data:
            lang_names = update_data.pop("languages")
            task.languages = await self._resolve_languages(lang_names)
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
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def _resolve_languages(self, lang_names: List[str]):
        languages = await self.lang_repo.get_by_names(lang_names)
        found = {l.language for l in languages}
        requested = set(lang_names)
        if found != requested:
            raise InvalidLanguageException()
        return languages

    async def get_filtered_tasks(self, filters: TaskFilter):
        return await self.repo.get_filtered(filters)

    async def delete_task(self, task_id: int) -> None:
        task = await self._get_task_or_raise(task_id)
        await self.repo.delete(task)
        await self.db.commit()

    async def _get_task_or_raise(self, task_id: int) -> Task:
        task = await self.repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException(f"Задача {task_id} не найдена")
        return task


def get_task_service(
    db: AsyncSession = Depends(session_generator),
    repo: TaskRepository = Depends(get_task_repository),
    lang_repo: LanguageRepository = Depends(get_language_repository),
) -> TaskService:
    return TaskService(db, repo, lang_repo)
