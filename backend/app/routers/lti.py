from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lti", tags=["lti"])


@router.post("/launch", summary="LTI Launch Endpoint")
async def lti_launch(request: Request):
    form_data = await request.form()

    print("=== LTI LAUNCH ===")
    for key, value in form_data.items():
        print(f"{key}: {value}")
    return RedirectResponse(url="http://localhost", status_code=303)
