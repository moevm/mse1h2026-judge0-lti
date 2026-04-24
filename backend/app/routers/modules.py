from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from app.schemas.module import ModuleWithTaskIdResponse, ModuleResponse
from app.schemas.task import TaskResponse
from app.services.module import (
    get_module_service,
    ModuleService,
    ModuleNotFoundException,
)
from app.mappers.module import ModuleMapper

router = APIRouter(prefix="/modules", tags=["modules"])


@router.get(
    "/",
    response_model=List[ModuleWithTaskIdResponse],
    summary="Получить список модулей",
)
def get_modules(
    service: ModuleService = Depends(get_module_service),
) -> List[ModuleWithTaskIdResponse]:
    modules = service.get_all_modules()
    return [ModuleMapper.to_module_with_task_ids(m) for m in modules]


@router.get(
    "/{module_id}",
    response_model=ModuleResponse,
    summary="Получить конкретный модуль по ID",
)
def get_module(
    module_id: int,
    service: ModuleService = Depends(get_module_service),
) -> ModuleResponse:
    try:
        module = service.get_module_by_id(module_id)
    except ModuleNotFoundException:
        raise HTTPException(status_code=404, detail="Модуль не найден")
    return ModuleMapper.to_module_with_tasks(module)


@router.get(
    "/{module_id}/tasks",
    response_model=List[TaskResponse],
    summary="Получить задачи модуля по ID",
)
def get_module_tasks(
    module_id: int,
    service: ModuleService = Depends(get_module_service),
) -> List[TaskResponse]:
    try:
        tasks = service.get_module_tasks(module_id)
    except ModuleNotFoundException:
        raise HTTPException(status_code=404, detail="Модуль не найден")
    return ModuleMapper.to_task_list(tasks)
