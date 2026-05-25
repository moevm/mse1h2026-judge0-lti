from fastapi import APIRouter, Depends

from app.schemas.check import (
    CheckRequest,
    CheckResponse,
    AttemptsInfoResponse,
    SubmitResponse,
    ResultRequest,
)
from app.services.check import CheckService, get_check_service
from app.mappers.check import CheckMapper
from app.core.dependencies import get_current_user_payload
from app.schemas.auth import TokenUser

router = APIRouter(prefix="/check", tags=["check"])


@router.post("/{task_id}/submit", response_model=SubmitResponse)
async def submit_solution(
    task_id: int,
    body: CheckRequest,
    user: TokenUser = Depends(get_current_user_payload),
    service: CheckService = Depends(get_check_service),
) -> SubmitResponse:
    ctx = await service.submit(task_id, user.user_id, body)
    return SubmitResponse(
        tokens=ctx.tokens,
        task_id=ctx.task_id,
        user_id=ctx.user_id,
        solution_id=ctx.solution_id,
        language_id=ctx.language_id,
        language=ctx.language,
    )


@router.post("/{task_id}/result", response_model=CheckResponse)
async def get_result(
    task_id: int,
    body: ResultRequest,
    user: TokenUser = Depends(get_current_user_payload),
    service: CheckService = Depends(get_check_service),
) -> CheckResponse:
    result = await service.get_result(task_id, user.user_id, body)
    if result is None:
        return CheckResponse(done=False)
    return CheckMapper.to_response(result)


@router.get("/{task_id}/attempts", response_model=AttemptsInfoResponse)
async def get_attempts_info(
    task_id: int,
    user: TokenUser = Depends(get_current_user_payload),
    service: CheckService = Depends(get_check_service),
) -> AttemptsInfoResponse:
    result = await service.get_attempts_info(task_id, user.user_id)
    return CheckMapper.to_attempts_response(result)
