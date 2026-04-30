from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Literal
from datetime import datetime

from app.services.analytics import (
    AnalyticsService, get_analytics_service,
    AttemptNotFoundException
)
from app.schemas.analytics import (
    UserModuleResponse, UserTaskResponse, AttemptResponse,
    UserModulesFilter, UserTasksFilter, AttemptsFilter
)
from app.core.dependencies import get_current_user_payload
from app.schemas.auth import TokenUser

router = APIRouter(tags=["analytics"])


@router.get("/users/{user_id}/modules", response_model=list[UserModuleResponse])
def get_user_modules(
    user_id: int,
    search: Optional[str] = Query(None),
    sort_by: Literal["name", "tasks_count", "created_at"] = Query("created_at"),
    sort_order: Literal["asc", "desc"] = Query("asc"),
    current_user: TokenUser = Depends(get_current_user_payload),
    service: AnalyticsService = Depends(get_analytics_service),
):
    # if current_user.role == "student" and current_user.id != user_id:
    #     raise HTTPException(status_code=403, detail="Доступ запрещён")

    # if current_user.role == "teacher":
    #     if not service.is_my_student(current_user.id, user_id):
    #         raise HTTPException(status_code=403, detail="Доступ запрещён")
    filters = UserModulesFilter(search=search, sort_by=sort_by, sort_order=sort_order)
    return service.get_user_modules(user_id, filters)


@router.get("/users/{user_id}/modules/{module_id}/tasks", response_model=list[UserTaskResponse])
def get_user_tasks_in_module(
    user_id: int,
    module_id: int,
    search: Optional[str] = Query(None),
    attempt_count_min: Optional[int] = Query(None, ge=0),
    status: Optional[Literal["passed", "failed"]] = Query(None),
    last_attempt_from: Optional[datetime] = Query(None),
    last_attempt_to: Optional[datetime] = Query(None),
    test_count_min: Optional[int] = Query(None, ge=0),
    sort_by: Literal["title", "attempt_count", "last_attempt_at", "test_count"] = Query("title"),
    sort_order: Literal["asc", "desc"] = Query("asc"),
    current_user: TokenUser = Depends(get_current_user_payload),
    service: AnalyticsService = Depends(get_analytics_service),
):
    filters = UserTasksFilter(
        search=search,
        attempt_count_min=attempt_count_min,
        status=status,
        last_attempt_from=last_attempt_from,
        last_attempt_to=last_attempt_to,
        test_count_min=test_count_min,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return service.get_user_tasks_in_module(user_id, module_id, filters)


@router.get("/tasks/{task_id}/attempts", response_model=list[AttemptResponse])
def get_task_attempts(
    task_id: int,
    user_id: int = Query(...),
    status: Optional[Literal["passed", "failed"]] = Query(None),
    language: Optional[str] = Query(None),
    memory_min: Optional[int] = Query(None, ge=0),
    memory_max: Optional[int] = Query(None, ge=0),
    time_min: Optional[int] = Query(None, ge=0),
    time_max: Optional[int] = Query(None, ge=0),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    current_user: TokenUser = Depends(get_current_user_payload),
    service: AnalyticsService = Depends(get_analytics_service),
):
    filters = AttemptsFilter(
        status=status,
        language=language,
        memory_min=memory_min,
        memory_max=memory_max,
        time_min=time_min,
        time_max=time_max,
        from_date=from_date,
        to_date=to_date,
    )
    return service.get_task_attempts(task_id, user_id, filters)


@router.get("/attempts/{attempt_id}", response_model=AttemptResponse)
def get_attempt(
    attempt_id: int,
    current_user: TokenUser = Depends(get_current_user_payload),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return service.get_attempt_by_id(attempt_id)
    except AttemptNotFoundException:
        raise HTTPException(status_code=404, detail="Попытка не найдена")
