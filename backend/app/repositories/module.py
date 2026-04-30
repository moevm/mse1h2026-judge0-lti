from typing import List

from fastapi import Depends
from sqlalchemy import select, delete, func, update, case, and_, asc, desc, or_
from sqlalchemy.orm import Session, selectinload

from app.database.database import session_generator
from app.database.models import Module, ModuleTaskOrder, Task
from app.schemas.module import ModuleFilter


class ModuleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, filters: ModuleFilter) -> List[Module]:
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
        return self.db.scalars(query).all()

    def get_by_id(self, module_id: int) -> Module | None:
        query = (
            select(Module)
            .options(selectinload(Module.task_links).selectinload(ModuleTaskOrder.task))
            .where(Module.id == module_id)
        )
        return self.db.scalars(query).first()

    def get_tasks(self, module_id: int) -> List[Task]:
        query = (
            select(Task)
            .join(ModuleTaskOrder)
            .where(ModuleTaskOrder.module_id == module_id)
            .order_by(ModuleTaskOrder.order)
        )
        return self.db.scalars(query).all()

    def get_module_task_ids(self, module_id: int) -> set[int]:
        query = select(ModuleTaskOrder.task_id).where(
            ModuleTaskOrder.module_id == module_id
        )
        return set(self.db.scalars(query).all())

    def get_max_order(self, module_id: int) -> int:
        query = select(func.max(ModuleTaskOrder.order)).where(
            ModuleTaskOrder.module_id == module_id
        )
        max_order = self.db.scalar(query)
        return max_order or 0

    def get_existing_task_ids(self, task_ids: List[int]) -> set[int]:
        query = select(Task.id).where(Task.id.in_(task_ids))
        return set(self.db.scalars(query).all())

    def add_task_to_module(self, link: ModuleTaskOrder) -> None:
        self.db.add(link)

    def create(self, module: Module) -> Module:
        self.db.add(module)
        self.db.flush()
        return module

    def delete(self, module: Module) -> None:
        self.db.delete(module)

    def get_module_task_link(self, module_id: int, task_id: int) -> ModuleTaskOrder:
        query = select(ModuleTaskOrder).where(
            ModuleTaskOrder.module_id == module_id, ModuleTaskOrder.task_id == task_id
        )
        return self.db.scalar(query)

    def get_module_task_links(self, module_id: int) -> List[ModuleTaskOrder]:
        return self.db.scalars(
            select(ModuleTaskOrder).where(ModuleTaskOrder.module_id == module_id)
        ).all()

    def get_module_task_links_dict(self, module_id: int):
        return {l.task_id: l for l in self.get_module_task_links(module_id)}

    def reorder_module_tasks(self, module_id: int, mapping: dict[int, int]) -> None:
        query = (
            update(ModuleTaskOrder)
            .where(ModuleTaskOrder.module_id == module_id)
            .values(order=case(mapping, value=ModuleTaskOrder.task_id))
        )
        self.db.execute(query)

    def shift_orders_after(self, module_id: int, order: int) -> None:
        self.db.execute(
            update(ModuleTaskOrder)
            .where(
                ModuleTaskOrder.module_id == module_id, ModuleTaskOrder.order > order
            )
            .values(order=ModuleTaskOrder.order - 1)
        )

    def delete_link(self, module_id: int, task_id: int) -> None:
        self.db.execute(
            delete(ModuleTaskOrder).where(
                ModuleTaskOrder.module_id == module_id,
                ModuleTaskOrder.task_id == task_id,
            )
        )

    def flush(self):
        self.db.flush()

    def refresh(self, module: Module):
        self.db.refresh(module)


def get_module_repository(db: Session = Depends(session_generator)):
    return ModuleRepository(db)
