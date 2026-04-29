from typing import List
from fastapi import Depends
from app.database.models import Module, Task
from app.repositories.module import ModuleRepository, get_module_repository
from app.schemas.module import ModulePatch, ModuleCreate


class ModuleNotFoundException(Exception):
    pass


class ModuleService:
    def __init__(self, repo: ModuleRepository):
        self.repo = repo

    def get_all_modules(self) -> List[Module]:
        modules = self.repo.get_all()
        return modules

    def get_module_by_id(self, module_id: int) -> Module:
        module = self.repo.get_by_id(module_id)
        if not module:
            raise ModuleNotFoundException
        return module

    def get_module_tasks(self, module_id: int) -> List[Task]:
        tasks = self.repo.get_tasks(module_id)
        return tasks

    def create_module(self, body: ModuleCreate) -> Module | None:
        module = self.repo.create(Module(title=body.title, description=body.description))
        return module

    def delete_module(self, module_id: int) -> None:
        module = self.repo.get_by_id(module_id)
        if not module:
            raise ModuleNotFoundException
        self.repo.delete(module)

    def patch_module(self, module_id: int, body: ModulePatch) -> Module:
        module = self.repo.get_by_id(module_id)
        if not module:
            raise ModuleNotFoundException
        if body.title is not None:
            module.title = body.title
        if body.description is not None:
            module.description = body.description
        self.repo.save(module)
        return module


def get_module_service(
    repo: ModuleRepository = Depends(get_module_repository),
) -> ModuleService:
    return ModuleService(repo)
