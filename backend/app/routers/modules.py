from typing import List
from fastapi import APIRouter
from fastapi.params import Depends

from app.schemas.module import (
    ModuleWithTaskIdResponse,
    ModuleResponse,
    ModulePatch,
    ModuleAddTasks,
    ModuleTasksReorder,
    ModuleFilter,
)
from app.schemas.task import TaskResponse
from app.services.module import get_module_service, ModuleService
from app.mappers.module import ModuleMapper
from app.schemas.module import ModuleCreate
from app.core.dependencies import get_current_admin
from app.schemas.auth import TokenUser

router = APIRouter(prefix="/modules", tags=["modules"])


@router.get(
    "/",
    response_model=List[ModuleWithTaskIdResponse],
    summary="Получить список модулей",
)
def get_modules(
    filters: ModuleFilter = Depends(),
    service: ModuleService = Depends(get_module_service),
) -> List[ModuleWithTaskIdResponse]:
    modules = service.get_all_modules(filters)
    return [ModuleMapper.to_module_with_task_ids(m) for m in modules]


@router.post("/", response_model=ModuleResponse, summary="Создать новый модуль")
async def create_module(
    body: ModuleCreate,
    admin: TokenUser = Depends(get_current_admin),
    service: ModuleService = Depends(get_module_service),
):
    return ModuleMapper.to_module_with_tasks(service.create_module(body))


@router.get(
    "/{module_id}",
    response_model=ModuleResponse,
    summary="Получить конкретный модуль по ID",
)
async def get_module(
    module_id: int,
    service: ModuleService = Depends(get_module_service),
) -> ModuleResponse:
    module = service.get_module_by_id(module_id)
    return ModuleMapper.to_module_with_tasks(module)


@router.delete(
    "/{module_id}",
    status_code=204,
    summary="Удалить конкретный модуль по ID",
)
async def delete_module(
    module_id: int,
    admin: TokenUser = Depends(get_current_admin),
    service: ModuleService = Depends(get_module_service),
):
    service.delete_module(module_id)


@router.get(
    "/{module_id}/tasks",
    response_model=List[TaskResponse],
    summary="Получить задачи модуля по ID",
)
async def get_module_tasks(
    module_id: int,
    service: ModuleService = Depends(get_module_service),
) -> List[TaskResponse]:
    tasks = service.get_module_tasks(module_id)
    return ModuleMapper.to_task_list(tasks)


@router.patch(
    "/{module_id}",
    response_model=ModuleResponse,
    summary="Изменить конкретный модуль по ID",
)
async def patch_module(
    module_id: int,
    body: ModulePatch,
    admin: TokenUser = Depends(get_current_admin),
    service: ModuleService = Depends(get_module_service),
) -> ModuleResponse:
    module = service.patch_module(module_id, body)
    return ModuleMapper.to_module_with_tasks(module)


@router.post(
    "/{module_id}/tasks",
    response_model=ModuleResponse,
    summary="Добавить задачи в модуль",
)
async def add_tasks_in_module(
    module_id: int,
    body: ModuleAddTasks,
    admin: TokenUser = Depends(get_current_admin),
    service: ModuleService = Depends(get_module_service),
) -> ModuleResponse:
    return ModuleMapper.to_module_with_tasks(service.add_tasks(module_id, body))


@router.delete(
    "/{module_id}/tasks/{task_id}",
    response_model=ModuleResponse,
    summary="Отвязать задачу от модуля",
)
async def remove_task_from_module(
    module_id: int,
    task_id: int,
    admin: TokenUser = Depends(get_current_admin),
    service: ModuleService = Depends(get_module_service),
):
    return ModuleMapper.to_module_with_tasks(
        service.remove_task_from_module(module_id, task_id)
    )


@router.patch(
    "/{module_id}/tasks/reorder",
    response_model=ModuleResponse,
    summary="Изменить порядок задач в модуле",
)
async def reorder_tasks_in_module(
    module_id: int,
    body: ModuleTasksReorder,
    admin: TokenUser = Depends(get_current_admin),
    service: ModuleService = Depends(get_module_service),
):
    return ModuleMapper.to_module_with_tasks(
        service.reorder_tasks_in_module(module_id, body)
    )
