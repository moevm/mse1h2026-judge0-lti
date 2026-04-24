import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.schemas.task import TaskResponse, TaskCreate, TaskFilter
from app.services.task import (
    get_task_service,
    TaskNotFoundException,
    InvalidLanguageException,
)
from app.services.task import TaskService
from app.mappers.task import TaskMapper
from app.schemas.task import TaskPatch
from app.services.task_test import (
    TaskTestService,
    get_task_test_service,
    TaskTestNotFoundException,
)

from app.schemas.task_test import (
    TaskTestFileSchema,
    TaskTestCreate,
    TaskTestResponse,
    TaskTestPatch,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "/", response_model=List[TaskResponse], summary="Получить список всех задач"
)
def get_tasks(
    filters: TaskFilter = Depends(), service: TaskService = Depends(get_task_service)
) -> List[TaskResponse]:
    tasks = service.get_filtered_tasks(filters)
    return TaskMapper.to_task_list_response(tasks)


@router.get("/{task_id}", response_model=TaskResponse, summary="Получить задачу по ID")
async def get_task(task_id: int, service: TaskService = Depends(get_task_service)):
    try:
        task = service.get_task_by_id(task_id)
    except TaskNotFoundException:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return TaskMapper.to_task_response(task)


@router.patch("/{task_id}", response_model=TaskResponse, summary="Изменить задачу")
async def patch_task(
    task_id: int, body: TaskPatch, service: TaskService = Depends(get_task_service)
):
    try:
        task = service.update_task(task_id, body)
    except TaskNotFoundException:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    except InvalidLanguageException:
        raise HTTPException(
            status_code=400, detail="Указан недопустимый язык программирования"
        )
    return TaskMapper.to_task_response(task)


@router.post("/", response_model=TaskResponse, summary="Создать задачу")
async def create_task(
    body: TaskCreate, service: TaskService = Depends(get_task_service)
):
    try:
        task = service.create_task(body)
    except InvalidLanguageException:
        raise HTTPException(
            status_code=400, detail="Указан недопустимый язык программирования"
        )
    return TaskMapper.to_task_response(task)


@router.delete("/{task_id}", status_code=204, summary="Удалить задачу")
async def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    try:
        service.delete_task(task_id)
    except TaskNotFoundException:
        raise HTTPException(status_code=404, detail="Задача не найдена")


@router.get(
    "/{task_id}/tests",
    response_model=List[TaskTestResponse],
    summary="Получить тесты задачи",
)
async def get_task_test(
    task_id: int, service: TaskTestService = Depends(get_task_test_service)
):
    try:
        tests = service.get_tests(task_id)
    except TaskNotFoundException:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return tests


@router.post(
    "/{task_id}/tests",
    response_model=TaskTestResponse,
    summary="Создать новый тест для задачи",
)
async def create_task_test(
    task_id: int,
    body: TaskTestCreate,
    service: TaskTestService = Depends(get_task_test_service),
) -> TaskTestResponse:
    try:
        test = service.create_test(task_id, body)
    except TaskNotFoundException:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return test


@router.delete(
    "/{task_id}/tests/{test_id}",
    status_code=204,
    summary="Удалить тест",
)
async def delete_task_test(
    task_id: int,
    test_id: int,
    service: TaskTestService = Depends(get_task_test_service),
):
    try:
        service.delete_test(task_id, test_id)
    except TaskNotFoundException:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    except TaskTestNotFoundException:
        raise HTTPException(status_code=404, detail="Тест не найден")


@router.post(
    "/{task_id}/tests/import",
    response_model=List[TaskTestResponse],
    summary="Загрузить тесты из JSON файла",
)
async def upload_task_tests(
    task_id: int,
    file: UploadFile = File(...),
    service: TaskTestService = Depends(get_task_test_service),
):
    try:
        content = await file.read()
        data = json.loads(content)
        parsed = TaskTestFileSchema.model_validate(data)
        tests = service.create_tests_bulk(task_id, parsed)
        return tests

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Некорректный JSON файл")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{task_id}/tests/{test_id}",
    response_model=TaskTestResponse,
    summary="Изменить тест",
)
async def patch_task_test(
    task_id: int,
    test_id: int,
    body: TaskTestPatch,
    service: TaskTestService = Depends(get_task_test_service),
):
    try:
        test = service.update_test(task_id, test_id, body)
    except TaskNotFoundException:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    except TaskTestNotFoundException:
        raise HTTPException(status_code=404, detail="Тест не найден")
    return test
