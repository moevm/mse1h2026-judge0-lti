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
from app.mappers.analytics import AnalyticsMapper

router = APIRouter(tags=["analytics"])


@router.get("/users/{user_id}/modules", response_model=list[UserModuleResponse])
def get_user_modules(
    user_id: int,
    filters: UserModulesFilter = Depends(),
    current_user: TokenUser = Depends(get_current_user_payload),
    service: AnalyticsService = Depends(get_analytics_service),
):
    # if current_user.role == "student" and current_user.id != user_id:
    #     raise HTTPException(status_code=403, detail="Доступ запрещён")

    # if current_user.role == "teacher":
    #     if not service.is_my_student(current_user.id, user_id):
    #         raise HTTPException(status_code=403, detail="Доступ запрещён")
    rows = service.get_user_modules(user_id, filters)
    return [AnalyticsMapper.to_module_response(module, task_count) for module, task_count in rows]


@router.get("/users/{user_id}/modules/{module_id}/tasks", response_model=list[UserTaskResponse])
def get_user_tasks_in_module(
    user_id: int,
    module_id: int,
    filters: UserTasksFilter = Depends(),
    current_user: TokenUser = Depends(get_current_user_payload),
    service: AnalyticsService = Depends(get_analytics_service),
):
    rows = service.get_user_tasks_in_module(user_id, module_id, filters)
    return [AnalyticsMapper.to_task_response(task, solution, attempt_count, last_attempt_at, test_count)
            for task, solution, attempt_count, last_attempt_at, test_count in rows]


@router.get("/tasks/{task_id}/attempts", response_model=list[AttemptResponse])
def get_task_attempts(
    task_id: int,
    user_id: int,
    filters: AttemptsFilter = Depends(),
    current_user: TokenUser = Depends(get_current_user_payload),
    service: AnalyticsService = Depends(get_analytics_service),
):
    attempts = service.get_task_attempts(task_id, user_id, filters)
    return [AnalyticsMapper.to_attempt_response(a) for a in attempts]


@router.get("/attempts/{attempt_id}", response_model=AttemptResponse)
def get_attempt(
    attempt_id: int,
    current_user: TokenUser = Depends(get_current_user_payload),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        attempt = service.get_attempt_by_id(attempt_id)
        return AnalyticsMapper.to_attempt_response(attempt)
    except AttemptNotFoundException:
        raise HTTPException(status_code=404, detail="Попытка не найдена")
