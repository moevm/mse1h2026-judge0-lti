from fastapi import APIRouter, Depends, HTTPException
from app.schemas.task import TaskResponse
from app.services.task import get_task_service, TaskNotFoundException
from app.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskResponse, summary="Получить задачу по ID")
async def get_task(task_id: int, service: TaskService = Depends(get_task_service)):
    try:
        task = service.get_task_by_id(task_id)
    except TaskNotFoundException:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task
