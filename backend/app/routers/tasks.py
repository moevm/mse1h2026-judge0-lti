from typing import List

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.task import TaskResponse, TaskCreate, TaskTestCreate, TaskTestResponse
from app.services.task import (
    get_task_service,
    TaskNotFoundException,
    InvalidLanguageException,
)
from app.services.task import TaskService
from app.mappers.task import TaskMapper
from app.schemas.task import TaskPatch

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "/", response_model=List[TaskResponse], summary="Получить список всех задач"
)
def get_tasks(service: TaskService = Depends(get_task_service)) -> List[TaskResponse]:
    tasks = service.get_all_tasks()
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
    "/{task_id}/tests", response_model=List[TaskTestResponse], summary="Получить тесты задачи"
)
async def get_task_test(task_id: int, service: TaskService = Depends(get_task_service)):
    try:
        tests = service.get_task_tests(task_id)
    except TaskNotFoundException:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return tests


@router.post(
    "/{task_id}/tests",
    response_model=List[TaskTestResponse],
    summary="Создать новый тест для задачи",
)
async def create_task_test(
    task_id: int, body: TaskTestCreate, service: TaskService = Depends(get_task_service)
) -> List[TaskTestResponse]:
    try:
        task = service.create_task_test(task_id, body)
    except TaskNotFoundException:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return TaskMapper.to_task_tests_list_response(task)
