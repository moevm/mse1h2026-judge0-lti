from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database.models import Module, Task, ModuleTaskOrder
from app.database.database import session_generator
from app.schemas.module import ModuleResponse, ModuleWithTaskIdResponse
from app.schemas.task import TaskResponse


class ModuleNotFoundException(Exception):
    pass


class ModuleService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_modules(self) -> List[ModuleWithTaskIdResponse]:
        modules = (
            self.db.query(Module)
            .options(selectinload(Module.task_links).selectinload(ModuleTaskOrder.task))
            .all()
        )
        return [
            ModuleWithTaskIdResponse(
                id=m.id,
                title=m.title,
                description=m.description,
                created_at=m.created_at,
                updated_at=m.updated_at,
                tasks=[link.task_id for link in m.task_links],
            )
            for m in modules
        ]
    def get_module_by_id(self, module_id: int) -> ModuleResponse:
        module = (
            self.db.query(Module)
            .options(selectinload(Module.task_links).selectinload(ModuleTaskOrder.task))
            .filter(Module.id == module_id)
            .first()
        )
        if not module:
            raise ModuleNotFoundException
        return ModuleResponse(
            id=module.id,
            title=module.title,
            description=module.description,
            created_at=module.created_at,
            updated_at=module.updated_at,
            tasks=[
                TaskResponse.model_validate(link.task) for link in module.task_links
            ],
        )

    def get_module_tasks(self, module_id: int) -> List[TaskResponse]:

        tasks = (
            self.db.query(Task)
            .join(ModuleTaskOrder)
            .filter(ModuleTaskOrder.module_id == module_id)
            .order_by(ModuleTaskOrder.order)
            .all()
        )
        return [TaskResponse.model_validate(t) for t in tasks]


def get_module_service(db: Session = Depends(session_generator)) -> ModuleService:
    return ModuleService(db)
