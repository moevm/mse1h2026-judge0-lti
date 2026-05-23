from typing import List
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.modules import (
    ModuleNotFoundException,
    DuplicateTaskInRequestException,
    TaskNotExistsException,
    TaskAlreadyInModuleException,
    ModuleTasksMismatchException,
)
from app.database.database import session_generator
from app.database.models import Module, Task, ModuleTaskOrder
from app.repositories.module import ModuleRepository, get_module_repository
from app.schemas.module import (
    ModulePatch,
    ModuleCreate,
    ModuleAddTasks,
    ModuleTasksReorder,
    ModuleFilter,
)


class ModuleService:
    def __init__(self,db: AsyncSession, repo: ModuleRepository):
        self.db = db
        self.repo = repo

    async def get_all_modules(self, filters: ModuleFilter) -> List[Module]:
        return await self.repo.get_all(filters)

    async def get_module_by_id(self, module_id: int) -> Module:
        return await self._get_module_or_raise(module_id)

    async def get_module_tasks(self, module_id: int) -> List[Task]:
        await self._get_module_or_raise(module_id)
        return await self.repo.get_tasks(module_id)

    async def create_module(self, body: ModuleCreate) -> Module | None:
        module = await self.repo.create(
            Module(**body.model_dump())
        )
        await self.db.commit()
        await self.db.refresh(module)
        return await self.repo.get_by_id(module.id)

    async def delete_module(self, module_id: int) -> None:
        module = await self._get_module_or_raise(module_id)
        await self.repo.delete(module)
        await self.db.commit()

    async def patch_module(self, module_id: int, body: ModulePatch) -> Module:
        module = await self._get_module_or_raise(module_id)
        data = body.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(module, key, value)
        await self.db.commit()
        await self.db.refresh(module)
        return module

    async def add_tasks(self, module_id: int, body: ModuleAddTasks) -> Module:
        module = await self._get_module_or_raise(module_id)
        if len(body.task_ids) != len(set(body.task_ids)):
            raise DuplicateTaskInRequestException()
        existing_task_ids = await self.repo.get_existing_task_ids(body.task_ids)
        if len(existing_task_ids) != len(body.task_ids):
            raise TaskNotExistsException()
        module_task_ids = await self.repo.get_module_task_ids(module_id)
        if any(task_id in module_task_ids for task_id in body.task_ids):
            raise TaskAlreadyInModuleException()
        max_order = await self.repo.get_max_order(module_id)
        for i, task_id in enumerate(body.task_ids):
            link = ModuleTaskOrder(
                module_id=module_id,
                task_id=task_id,
                order=max_order + i + 1,
            )
            await self.repo.add_task_to_module(link)
        await self.db.commit()
        return await self.repo.get_by_id(module_id)

    async def remove_task_from_module(self, module_id: int, task_id: int) -> Module:
        module = await self._get_module_or_raise(module_id)
        link = await self.repo.get_module_task_link(module_id, task_id)
        if not link:
            raise TaskNotExistsException()
        await self.repo.delete_link(module_id, task_id)
        await self.repo.shift_orders_after(module_id, link.order)
        await self.db.commit()
        self.db.expire(module)
        return await self.repo.get_by_id(module_id)

    async def reorder_tasks_in_module(
        self, module_id: int, body: ModuleTasksReorder
    ) -> Module:
        module = await self._get_module_or_raise(module_id)
        task_ids = [t.task_id for t in body.tasks]
        if len(task_ids) != len(set(task_ids)):
            raise DuplicateTaskInRequestException()
        links = await self.repo.get_module_task_links_dict(module_id)
        incoming_ids = set(task_ids)
        if incoming_ids != set(links.keys()):
            raise ModuleTasksMismatchException()
        mapping = body.to_mapping()
        await self.repo.reorder_module_tasks(module_id, mapping)
        await self.db.commit()
        self.db.expire(module)
        return await self.repo.get_by_id(module_id)

    async def _get_module_or_raise(self, module_id: int) -> Module:
        module = await self.repo.get_by_id(module_id)
        if not module:
            raise ModuleNotFoundException(f"Модуль {module_id} не найден")
        return module


def get_module_service(
    db: AsyncSession = Depends(session_generator),
    repo: ModuleRepository = Depends(get_module_repository),
) -> ModuleService:
    return ModuleService(db, repo)
