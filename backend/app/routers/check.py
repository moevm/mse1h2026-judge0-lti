from fastapi import APIRouter, Depends

from app.schemas.check import CheckRequest, CheckResponse
from app.services.check import (
    CheckService,
    get_check_service,
)
from app.mappers.check import CheckMapper
from app.core.dependencies import get_current_user_payload
from app.schemas.auth import TokenUser

router = APIRouter(prefix="/check", tags=["check"])


@router.post("/{task_id}", response_model=CheckResponse)
async def check_solution(
    task_id: int,
    body: CheckRequest,
    user: TokenUser = Depends(get_current_user_payload),
    service: CheckService = Depends(get_check_service),
) -> CheckResponse:
    result = await service.check_solution(task_id, user.user_id, body)
    return CheckMapper.to_response(result)
