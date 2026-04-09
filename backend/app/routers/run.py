from fastapi import HTTPException

from fastapi import APIRouter
from fastapi.params import Depends

from app.schemas.run import RunRequest, RunResponse
from app.services.run import RunService, get_run_service

router = APIRouter(prefix="/run", tags=["run"])


@router.post("/", response_model=RunResponse)
async def run_code(
    body: RunRequest,
    service: RunService = Depends(get_run_service),
) -> RunResponse:
    try:
        result = service.run_code(body)
    except:
        raise HTTPException("Error", 500)
    return RunResponse(
        stdout=result["stdout"],
        stderr=result["stderr"],
        compile_output=result["compile_output"],
    )
