import json
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import ValidationError
from app.database.models import UserTypeEnum
from app.schemas.task import TaskResponse, TaskCreate, TaskFilter
from app.services.task import get_task_service
from app.services.task import TaskService
from app.mappers.task import TaskMapper
from app.schemas.task import TaskPatch
from app.services.task_test import (
    TaskTestService,
    get_task_test_service,
)

from app.schemas.task_test import (
    TaskTestFileSchema,
    TaskTestCreate,
    TaskTestResponse,
    TaskTestPatch,
)
from app.core.dependencies import require_roles
from app.schemas.auth import TokenUser
from app.core.exceptions.tasks import InvalidTaskTestsFileException

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "/", response_model=List[TaskResponse], summary="Получить список всех задач"
)
async def get_tasks(
    filters: TaskFilter = Depends(),
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: TaskService = Depends(get_task_service),
) -> List[TaskResponse]:
    tasks = await service.get_filtered_tasks(filters)
    return TaskMapper.to_task_list_response(tasks)


@router.get("/{task_id}", response_model=TaskResponse, summary="Получить задачу по ID")
async def get_task(
    task_id: int,
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: TaskService = Depends(get_task_service),
):
    task = await service.get_task_by_id(task_id)
    return TaskMapper.to_task_response(task)


@router.patch("/{task_id}", response_model=TaskResponse, summary="Изменить задачу")
async def patch_task(
    task_id: int,
    body: TaskPatch,
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: TaskService = Depends(get_task_service),
):
    task = await service.update_task(task_id, body)
    return TaskMapper.to_task_response(task)


@router.post("/", response_model=TaskResponse, summary="Создать задачу")
async def create_task(
    body: TaskCreate,
    service: TaskService = Depends(get_task_service),
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
):
    task = await service.create_task(body)
    return TaskMapper.to_task_response(task)


@router.delete("/{task_id}", status_code=204, summary="Удалить задачу")
async def delete_task(
    task_id: int,
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: TaskService = Depends(get_task_service),
):
    await service.delete_task(task_id)


@router.get(
    "/{task_id}/tests",
    response_model=List[TaskTestResponse],
    summary="Получить тесты задачи",
)
async def get_task_test(
    task_id: int,
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: TaskTestService = Depends(get_task_test_service),
):
    return await service.get_tests(task_id)


@router.post(
    "/{task_id}/tests",
    response_model=TaskTestResponse,
    summary="Создать новый тест для задачи",
)
async def create_task_test(
    task_id: int,
    body: TaskTestCreate,
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: TaskTestService = Depends(get_task_test_service),
) -> TaskTestResponse:
    return await service.create_test(task_id, body)


@router.delete(
    "/{task_id}/tests/{test_id}",
    status_code=204,
    summary="Удалить тест",
)
async def delete_task_test(
    task_id: int,
    test_id: int,
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: TaskTestService = Depends(get_task_test_service),
):
    await service.delete_test(task_id, test_id)


@router.post(
    "/{task_id}/tests/import",
    response_model=List[TaskTestResponse],
    summary="Загрузить тесты из JSON файла",
)
async def upload_task_tests(
    task_id: int,
    file: UploadFile = File(...),
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: TaskTestService = Depends(get_task_test_service),
):
    try:
        content = await file.read()
        data = json.loads(content)
        parsed = TaskTestFileSchema.model_validate(data)
        tests = await service.create_tests_bulk(task_id, parsed)
        return tests

    except (json.JSONDecodeError, ValidationError):
        raise InvalidTaskTestsFileException()


@router.patch(
    "/{task_id}/tests/{test_id}",
    response_model=TaskTestResponse,
    summary="Изменить тест",
)
async def patch_task_test(
    task_id: int,
    test_id: int,
    body: TaskTestPatch,
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: TaskTestService = Depends(get_task_test_service),
):
    test = await service.update_test(task_id, test_id, body)
    return test
