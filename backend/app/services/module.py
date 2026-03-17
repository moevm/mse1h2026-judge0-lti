from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database.models import Module, Task, ModuleTaskOrder
from app.database.database import session_generator


class ModuleNotFoundException(Exception):
    pass


class ModuleService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_modules(self) -> List[Module]:
        return self.db.query(Module).options(joinedload(Module.tasks)).all()

    def get_module_by_id(self, module_id: int) -> Module:
        module = (
            self.db.query(Module)
            .options(joinedload(Module.tasks))
            .filter(Module.id == module_id)
            .first()
        )
        if not module:
            raise ModuleNotFoundException
        return module

    def get_module_tasks(self, module_id: int) -> List[Task]:
        module = self.db.query(Module).filter(Module.id == module_id).first()
        if not module:
            raise ModuleNotFoundException
        tasks = (
            self.db.query(Task)
            .options(selectinload(Task.languages))
            .join(ModuleTaskOrder, ModuleTaskOrder.task_id == Task.id)
            .filter(ModuleTaskOrder.module_id == module_id)
            .order_by(ModuleTaskOrder.order)
            .all()
        )
        return tasks


def get_module_service(db: Session = Depends(session_generator)) -> ModuleService:
    return ModuleService(db)
