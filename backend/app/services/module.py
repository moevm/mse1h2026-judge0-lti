from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database.models import Module, Task, ModuleTaskOrder
from app.schemas.module import ModuleResponse, ModuleWithTaskIdResponse
from app.schemas.task import TaskResponse
from app.repositories.module import ModuleRepository, get_module_repository
from app.mappers.module import ModuleMapper


class ModuleNotFoundException(Exception):
    pass


class ModuleService:
    def __init__(self, repo: ModuleRepository):
        self.repo = repo

    def get_all_modules(self) -> List[ModuleWithTaskIdResponse]:
        modules = self.repo.get_all()
        return [ModuleMapper.to_module_with_task_ids(m) for m in modules]

    def get_module_by_id(self, module_id: int):
        module = self.repo.get_by_id(module_id)
        if not module:
            raise ModuleNotFoundException
        return ModuleMapper.to_module_with_tasks(module)

    def get_module_tasks(self, module_id: int):
        tasks = self.repo.get_tasks(module_id)
        return ModuleMapper.to_task_list(tasks)


def get_module_service(
    repo: ModuleRepository = Depends(get_module_repository),
) -> ModuleService:
    return ModuleService(repo)
