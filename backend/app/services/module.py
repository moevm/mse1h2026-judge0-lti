from typing import List
from fastapi import Depends
from app.database.models import Module, Task, ModuleTaskOrder
from app.repositories.module import ModuleRepository, get_module_repository
from app.schemas.module import ModulePatch, ModuleCreate, ModuleAddTasks, ModuleTasksReorder


class ModuleNotFoundException(Exception):
    pass

class TaskNotExistsException(Exception):
    pass

class DuplicateTaskInRequestException(Exception):
    pass

class TaskAlreadyInModuleException(Exception):
    pass

class InvalidTaskOrderException(Exception):
    pass


class ModuleService:
    def __init__(self, repo: ModuleRepository):
        self.repo = repo

    def get_all_modules(self) -> List[Module]:
        return self.repo.get_all()

    def get_module_by_id(self, module_id: int) -> Module:
        return self._get_module_or_raise(module_id)

    def get_module_tasks(self, module_id: int) -> List[Task]:
        return self.repo.get_tasks(module_id)

    def create_module(self, body: ModuleCreate) -> Module | None:
        module = self.repo.create(Module(title=body.title, description=body.description))
        return module

    def delete_module(self, module_id: int) -> None:
        module = self._get_module_or_raise(module_id)
        self.repo.delete(module)

    def patch_module(self, module_id: int, body: ModulePatch) -> Module:
        module = self._get_module_or_raise(module_id)
        if body.title is not None:
            module.title = body.title
        if body.description is not None:
            module.description = body.description
        self.repo.flush()
        self.repo.refresh(module)
        return module

    def add_tasks(self, module_id: int, body: ModuleAddTasks) -> Module:
        module = self._get_module_or_raise(module_id)
        if len(body.task_ids) != len(set(body.task_ids)):
            raise DuplicateTaskInRequestException
        existing_task_ids = self.repo.get_existing_task_ids(body.task_ids)
        if len(existing_task_ids) != len(body.task_ids):
            raise TaskNotExistsException
        module_task_ids = self.repo.get_module_task_ids(module_id)
        if any(task_id in module_task_ids for task_id in body.task_ids):
            raise TaskAlreadyInModuleException
        max_order = self.repo.get_max_order(module_id)
        for i, task_id in enumerate(body.task_ids):
            link = ModuleTaskOrder(
                module_id=module_id,
                task_id=task_id,
                order=max_order + i + 1,
            )
            self.repo.add_task_to_module(link)
        self.repo.flush()
        self.repo.refresh(module)
        return module

    def remove_task_from_module(self, module_id: int, task_id: int) -> Module:
        module = self._get_module_or_raise(module_id)
        link = self.repo.get_module_task_link(module_id, task_id)
        if not link:
            raise TaskNotExistsException
        self.repo.delete_link(module_id, task_id)
        self.repo.shift_orders_after(module_id, link.order)
        self.repo.flush()
        self.repo.refresh(module)
        return module

    def reorder_tasks_in_module(
        self, module_id: int, body: ModuleTasksReorder
    ) -> Module:
        module = self._get_module_or_raise(module_id)
        task_ids = [t.task_id for t in body.tasks]
        if len(task_ids) != len(set(task_ids)):
            raise DuplicateTaskInRequestException
        links = self.repo.get_module_task_links_dict(module_id)
        incoming_ids = set(task_ids)
        if incoming_ids != set(links.keys()):
            raise TaskNotExistsException
        mapping = body.to_mapping()
        self.repo.reorder_module_tasks(module_id, mapping)
        self.repo.flush()
        self.repo.refresh(module)
        return module

    def _get_module_or_raise(self, module_id: int) -> Module:
        module = self.repo.get_by_id(module_id)
        if not module:
            raise ModuleNotFoundException
        return module


def get_module_service(
    repo: ModuleRepository = Depends(get_module_repository),
) -> ModuleService:
    return ModuleService(repo)
