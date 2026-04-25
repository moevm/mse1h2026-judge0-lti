from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.database import session_generator
from app.database.models import Module, ModuleTaskOrder, Task


class ModuleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Module]:
        query = select(Module).options(
            selectinload(Module.task_links).selectinload(ModuleTaskOrder.task)
        )
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


def get_module_repository(db: Session = Depends(session_generator)):
    return ModuleRepository(db)
