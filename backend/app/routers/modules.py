from typing import List
from fastapi import APIRouter
from fastapi.params import Depends

from app.database.models import UserTypeEnum
from app.mappers.module_session import ModuleSessionMapper
from app.schemas.module import (
    ModuleWithTaskIdResponse,
    ModuleResponse,
    ModulePatch,
    ModuleAddTasks,
    ModuleTasksReorder,
    ModuleFilter,
)
from app.schemas.module_session import ModuleSessionResponse
from app.schemas.task import TaskResponse
from app.services.module import get_module_service, ModuleService
from app.mappers.module import ModuleMapper
from app.schemas.module import ModuleCreate
from app.core.dependencies import get_current_user_payload, require_roles
from app.schemas.auth import TokenUser
from app.services.module_session import ModuleSessionService, get_module_session_service

router = APIRouter(prefix="/modules", tags=["modules"])


@router.get(
    "/",
    response_model=List[ModuleWithTaskIdResponse],
    summary="Получить список модулей",
)
async def get_modules(
    filters: ModuleFilter = Depends(),
    service: ModuleService = Depends(get_module_service),
) -> List[ModuleWithTaskIdResponse]:
    modules = await service.get_all_modules(filters)
    return [ModuleMapper.to_module_with_task_ids(m) for m in modules]


@router.post("/", response_model=ModuleResponse, summary="Создать новый модуль")
async def create_module(
    body: ModuleCreate,
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: ModuleService = Depends(get_module_service),
):
    return ModuleMapper.to_module_with_tasks(await service.create_module(body))


@router.get(
    "/{module_id}",
    response_model=ModuleResponse,
    summary="Получить конкретный модуль по ID",
)
async def get_module(
    module_id: int,
    service: ModuleService = Depends(get_module_service),
) -> ModuleResponse:
    module = await service.get_module_by_id(module_id)
    return ModuleMapper.to_module_with_tasks(module)


@router.delete(
    "/{module_id}",
    status_code=204,
    summary="Удалить конкретный модуль по ID",
)
async def delete_module(
    module_id: int,
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: ModuleService = Depends(get_module_service),
):
    await service.delete_module(module_id)


@router.get(
    "/{module_id}/tasks",
    response_model=List[TaskResponse],
    summary="Получить задачи модуля по ID",
)
async def get_module_tasks(
    module_id: int,
    service: ModuleService = Depends(get_module_service),
) -> List[TaskResponse]:
    tasks = await service.get_module_tasks(module_id)
    return ModuleMapper.to_task_list(tasks)


@router.patch(
    "/{module_id}",
    response_model=ModuleResponse,
    summary="Изменить конкретный модуль по ID",
)
async def patch_module(
    module_id: int,
    body: ModulePatch,
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: ModuleService = Depends(get_module_service),
) -> ModuleResponse:
    module = await service.patch_module(module_id, body)
    return ModuleMapper.to_module_with_tasks(module)


@router.post(
    "/{module_id}/tasks",
    response_model=ModuleResponse,
    summary="Добавить задачи в модуль",
)
async def add_tasks_in_module(
    module_id: int,
    body: ModuleAddTasks,
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: ModuleService = Depends(get_module_service),
) -> ModuleResponse:
    return ModuleMapper.to_module_with_tasks(await service.add_tasks(module_id, body))


@router.delete(
    "/{module_id}/tasks/{task_id}",
    response_model=ModuleResponse,
    summary="Отвязать задачу от модуля",
)
async def remove_task_from_module(
    module_id: int,
    task_id: int,
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: ModuleService = Depends(get_module_service),
):
    return ModuleMapper.to_module_with_tasks(
        await service.remove_task_from_module(module_id, task_id)
    )


@router.patch(
    "/{module_id}/tasks/reorder",
    response_model=ModuleResponse,
    summary="Изменить порядок задач в модуле",
)
async def reorder_tasks_in_module(
    module_id: int,
    body: ModuleTasksReorder,
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: ModuleService = Depends(get_module_service),
):
    return ModuleMapper.to_module_with_tasks(
        await service.reorder_tasks_in_module(module_id, body)
    )


@router.post(
    "/{module_id}/start",
    response_model=ModuleSessionResponse,
    summary="Старт прохождения модуля",
)
async def start_module_session(
    module_id: int,
    user: TokenUser = Depends(get_current_user_payload),
    service: ModuleSessionService = Depends(get_module_session_service),
):
    """
    Запускает (или возвращает уже существующую) сессию прохождения модуля.
    Сессия может быть:
    - ограниченной по времени (expires_at установлен)
    - без ограничения времени (expires_at = NULL)
    """
    session = await service.start_session(module_id, user)
    return ModuleSessionMapper.to_response(session)


@router.get(
    "/{module_id}/session",
    response_model=ModuleSessionResponse,
    summary="Получить активную сессию прохождения модуля (или её отсутствие)",
)
async def get_module_session(
    module_id: int,
    user: TokenUser = Depends(get_current_user_payload),
    service: ModuleSessionService = Depends(get_module_session_service),
):
    """
    Возвращает активную сессию пользователя для указанного модуля.
    Активной считается сессия, которая:
    - не завершена (finished_at IS NULL)
    - не истекла по времени (expires_at IS NULL или expires_at > now)
    
    Если активной сессии нет — возвращается {"session": null}.
    """
    session = await service.get_session(module_id, user)
    return ModuleSessionMapper.to_response(session)

@router.get("/{module_id}/session/finish", summary="Завершить активную сессию прохождения модуля")
async def finish_module_session(
    module_id: int,
    user: TokenUser = Depends(get_current_user_payload),
    service: ModuleSessionService = Depends(get_module_session_service),
):
    """
    Завершает активную сессию пользователя для указанного модуля.
    """
    session = await service.finish_session(module_id, user)
    return ModuleSessionMapper.to_response(session)