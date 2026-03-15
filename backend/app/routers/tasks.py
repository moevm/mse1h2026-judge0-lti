from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import session_generator
from app.database.models import Task
from app.schemas.task import TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/{task_id}", response_model=TaskResponse, summary="Получить задачу по ID")
async def get_task(task_id: int, db: Session = Depends(session_generator)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "timeout": task.timeout,
        "languages": [lang.language for lang in task.languages],
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }