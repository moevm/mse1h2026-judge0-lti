from fastapi import APIRouter, Request, Depends, Response
from fastapi.responses import RedirectResponse
from app.services.lti import LtiService, get_lti_service
from app.services.jwt import JwtService, get_jwt_service
from app.services.auth import AuthService, get_auth_service

router = APIRouter(prefix="/lti", tags=["lti"])


@router.post("/launch", summary="LTI Launch Endpoint")
async def lti_launch(
    request: Request,
    lti_service: LtiService = Depends(get_lti_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    form_data = await request.form()

    user_id = int(form_data.get("user_id"))
    username = form_data.get("ext_user_username", str(user_id))
    full_name = form_data.get("lis_person_name_full", f"User {user_id}")
    roles = form_data.get("roles", "Student")
    # print("=== LTI LAUNCH ===")
    # for key, value in form_data.items():
    #     print(f"{key}: {value}")
    user = lti_service.upsert_user(user_id, username, full_name, roles)
    access_token, refresh_token = auth_service.issue_lti_session(user)
    response = RedirectResponse(url="http://localhost/", status_code=303)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    # print(f"TOKEN: {token}")
    # print(f"id: {user_id}, name: {username}, fullname: {full_name}, roles: {roles}")
    return response
