from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from app.schemas.run import RunRequest, RunResponse
from app.services.run import RunService, get_run_service, LanguageNotFoundException
from app.services.judge import Judge0Exception

router = APIRouter(prefix="/run", tags=["run"])


@router.post("/", response_model=RunResponse, summary="Run code")
async def run_code(
    body: RunRequest,
    service: RunService = Depends(get_run_service),
) -> RunResponse:
    try:
        result = service.run_code(body)
    except LanguageNotFoundException as e:
        raise HTTPException(
            status_code=400, detail="Недопустимый язык программирования для этой задачи"
        )
    except Judge0Exception:
        raise HTTPException(status_code=500, detail="Ошибка связи с Judge0")
    return RunResponse(
        stdout=result.get("stdout"),
        stderr=result.get("stderr"),
        compile_output=result.get("compile_output"),
    )
