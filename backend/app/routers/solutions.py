from typing import List
from fastapi import APIRouter, Depends

from app.database.models import UserTypeEnum
from app.schemas.solution import SolutionFilter, SolutionWithUserResponse
from app.schemas.attempt import AttemptResponse
from app.services.solution import SolutionService, get_solution_service
from app.core.dependencies import require_roles
from app.schemas.auth import TokenUser
from app.mappers.solution import SolutionMapper

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
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: SolutionService = Depends(get_solution_service),
):
    solutions = await service.get_solutions_by_task(task_id, filters)
    return [SolutionMapper.to_solution_with_user_response(s) for s in solutions]


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
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: SolutionService = Depends(get_solution_service),
):
    attempts = await service.get_solution_attempts(solution_id)
    return [SolutionMapper.to_attempt_response(a) for a in attempts]
