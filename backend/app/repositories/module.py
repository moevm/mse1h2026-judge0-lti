from typing import List

from fastapi import Depends
from sqlalchemy import select, delete, func, update, case, and_, asc, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import session_generator
from app.database.models import Module, ModuleTaskOrder, Task
from app.schemas.module import ModuleFilter


class ModuleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, filters: ModuleFilter) -> List[Module]:
        query = select(Module).options(
            selectinload(Module.task_links).selectinload(ModuleTaskOrder.task)
        )
        conditions = []
        if filters.search:
            conditions.append(
                or_(
                    Module.title.ilike(f"%{filters.search}%"),
                    Module.description.ilike(f"%{filters.search}%"),
                )
            )
        if filters.created_from:
            conditions.append(Module.created_at >= filters.created_from)
        if filters.created_to:
            conditions.append(Module.created_at <= filters.created_to)
        if filters.updated_from:
            conditions.append(Module.updated_at >= filters.updated_from)
        if filters.updated_to:
            conditions.append(Module.updated_at <= filters.updated_to)
        if conditions:
            query = query.where(and_(*conditions))
        if filters.sort_by:
            column = getattr(Module, filters.sort_by)
            if filters.sort_order == "asc":
                query = query.order_by(asc(column))
            else:
                query = query.order_by(desc(column))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, module_id: int) -> Module | None:
        result = await self.db.execute(
            select(Module)
            .options(
                selectinload(Module.task_links)
                .selectinload(ModuleTaskOrder.task)
                .selectinload(Task.languages),
                selectinload(Module.task_links)
                .selectinload(ModuleTaskOrder.task)
                .selectinload(Task.tests),
            )
            .where(Module.id == module_id)
        )
        return result.scalars().first()

    async def get_tasks(self, module_id: int) -> List[Task]:
        result = await self.db.execute(
            select(Task)
            .options(
                selectinload(Task.languages),
                selectinload(Task.tests),
            )
            .join(ModuleTaskOrder)
            .where(ModuleTaskOrder.module_id == module_id)
            .order_by(ModuleTaskOrder.order)
        )
        return result.scalars().all()

    async def get_module_task_ids(self, module_id: int) -> set[int]:
        result = await self.db.execute(
            select(ModuleTaskOrder.task_id).where(ModuleTaskOrder.module_id == module_id)
        )
        return set(result.scalars().all())

    async def get_max_order(self, module_id: int) -> int:
        result = await self.db.scalar(
            select(func.max(ModuleTaskOrder.order)).where(ModuleTaskOrder.module_id == module_id)
        )
        return result or 0

    async def get_existing_task_ids(self, task_ids: List[int]) -> set[int]:
        result = await self.db.execute(
            select(Task.id).where(Task.id.in_(task_ids))
        )
        return set(result.scalars().all())

    async def add_task_to_module(self, link: ModuleTaskOrder) -> None:
        self.db.add(link)

    async def create(self, module: Module) -> Module:
        self.db.add(module)
        return module

    async def delete(self, module: Module) -> None:
        await self.db.delete(module)

    async def get_module_task_link(
        self, module_id: int, task_id: int
    ) -> ModuleTaskOrder | None:
        result = await self.db.scalar(
            select(ModuleTaskOrder).where(
                ModuleTaskOrder.module_id == module_id,
                ModuleTaskOrder.task_id == task_id,
            )
        )
        return result

    async def get_module_task_links(self, module_id: int) -> List[ModuleTaskOrder]:
        result = await self.db.execute(
            select(ModuleTaskOrder).where(ModuleTaskOrder.module_id == module_id)
        )
        return result.scalars().all()

    async def get_module_task_links_dict(
        self, module_id: int
    ) -> dict[int, ModuleTaskOrder]:
        links = await self.get_module_task_links(module_id)
        return {l.task_id: l for l in links}

    async def reorder_module_tasks(
        self, module_id: int, mapping: dict[int, int]
    ) -> None:
        await self.db.execute(
            update(ModuleTaskOrder)
            .where(ModuleTaskOrder.module_id == module_id)
            .values(order=case(mapping, value=ModuleTaskOrder.task_id))
        )

    async def shift_orders_after(self, module_id: int, order: int) -> None:
        await self.db.execute(
            update(ModuleTaskOrder)
            .where(
                ModuleTaskOrder.module_id == module_id,
                ModuleTaskOrder.order > order,
            )
            .values(order=ModuleTaskOrder.order - 1)
        )

    async def delete_link(self, module_id: int, task_id: int) -> None:
        link = await self.db.get(ModuleTaskOrder, (module_id, task_id))
        if link:
            await self.db.delete(link)


def get_module_repository(db: AsyncSession = Depends(session_generator)):
    return ModuleRepository(db)
