from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/lti", tags=["lti"])


@router.post("/launch", summary="LTI Launch Endpoint")
async def lti_launch():
    return RedirectResponse(url="http://localhost", status_code=303)
