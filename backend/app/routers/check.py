from fastapi import APIRouter, HTTPException, Depends

from app.schemas.check import CheckRequest, CheckResponse
from app.services.check import (
    CheckService,
    get_check_service,
    TaskNotFoundException,
    InvalidLanguageException,
    Judge0Exception,
)

router = APIRouter(prefix="/check", tags=["check"])


@router.post("/{task_id}", response_model=CheckResponse)
async def check_solution(
    task_id: int,
    body: CheckRequest,
    service: CheckService = Depends(get_check_service),
) -> CheckResponse:
    try:
        result = service.check_solution(task_id, body)
    except TaskNotFoundException:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    except InvalidLanguageException:
        raise HTTPException(
            status_code=400, detail="Недопустимый язык программирования для этой задачи"
        )
    except Judge0Exception:
        raise HTTPException(status_code=500, detail="Ошибка связи с Judge0")

    return CheckResponse(
        success=result.success,
        error=result.error,
        comment=result.comment,
        passed=f"{result.passed}/{result.total} тестов пройдено",
    )
