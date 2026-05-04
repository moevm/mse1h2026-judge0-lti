from fastapi import APIRouter, HTTPException, Depends

from app.schemas.check import CheckRequest, CheckResponse
from app.services.check import (
    CheckService,
    get_check_service,
    TaskNotFoundException,
    InvalidLanguageException,
)
from app.services.judge import Judge0Exception
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
    try:
        result = await service.check_solution(task_id, user.user_id, body)
    except TaskNotFoundException:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    except InvalidLanguageException:
        raise HTTPException(
            status_code=400, detail="Недопустимый язык программирования для этой задачи"
        )
    except Judge0Exception:
        raise HTTPException(status_code=500, detail="Ошибка связи с Judge0")

    return CheckMapper.to_response(result)
