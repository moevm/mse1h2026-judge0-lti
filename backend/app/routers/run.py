from fastapi import APIRouter
from fastapi.params import Depends

from app.schemas.run import RunRequest, RunResponse
from app.services.run import RunService, get_run_service

router = APIRouter(prefix="/run", tags=["run"])


@router.post("/", response_model=RunResponse, summary="Run code")
async def run_code(
    body: RunRequest,
    service: RunService = Depends(get_run_service),
) -> RunResponse:
    result = await service.run_code(body)
    return RunResponse(
        stdout=result.get("stdout"),
        stderr=result.get("stderr"),
        compile_output=result.get("compile_output"),
    )
