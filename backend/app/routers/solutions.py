from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.solution import SolutionFilter, SolutionWithUserResponse
from app.schemas.attempt import AttemptResponse
from app.services.solution import SolutionService, get_solution_service
from app.core.dependencies import get_current_admin
from app.schemas.auth import TokenUser
from app.core.exceptions.tasks import TaskNotFoundException

router = APIRouter(prefix="/solutions", tags=["solutions"])


@router.get(
    "/tasks/{task_id}",
    response_model=List[SolutionWithUserResponse],
    summary="Получить все решения для задачи",
    description=(
        "Возвращает список всех решений для указанной задачи с данными пользователя. "
        "Доступно только для администратора. "
        "Поддерживает фильтрацию:\n"
        "- **is_solved** - фильтр по статусу решения (true/false)\n"
        "- **score_min** - минимальный балл (включительно)\n"
        "- **score_max** - максимальный балл (включительно)\n"
        "- **updated_from** - начальная дата обновления\n"
        "- **updated_to** - конечная дата обновления\n"
        "- **sort_by** - поле для сортировки (id, score, is_solved, created_at, updated_at)\n"
        "- **sort_order** - направление сортировки (asc/desc)"
    ),
)
async def get_task_solutions(
    task_id: int,
    filters: SolutionFilter = Depends(),
    admin: TokenUser = Depends(get_current_admin),
    service: SolutionService = Depends(get_solution_service),
):
    solutions = service.get_solutions_by_task(task_id, filters)
    return [
        {
            "id": s.id,
            "task_id": s.task_id,
            "user_id": s.user_id,
            "username": s.user.username if s.user else None,
            "full_name": s.user.full_name if s.user else None,
            "is_solved": s.is_solved,
            "score": s.score,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }
        for s in solutions
    ]


@router.get(
    "/{solution_id}/attempts",
    response_model=List[AttemptResponse],
    summary="Получить все попытки решения",
    description=(
        "Возвращает список всех попыток (Attempt) для указанного решения. "
        "Каждая попытка содержит код, результат выполнения, ошибки, время и память. "
        "Доступно только для администратора. "
        "Попытки сортируются по дате создания (от старых к новым)."
    ),
)
async def get_solution_attempts(
    solution_id: int,
    admin: TokenUser = Depends(get_current_admin),
    service: SolutionService = Depends(get_solution_service),
):
    try:
        attempts = service.get_solution_attempts(solution_id)
    except TaskNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

    return attempts
