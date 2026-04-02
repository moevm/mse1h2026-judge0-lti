from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from app.services.lti import LtiServer, get_lti_service
from app.services.jwt import JwtService, get_jwt_service

router = APIRouter(prefix="/lti", tags=["lti"])


@router.post("/launch", summary="LTI Launch Endpoint")
async def lti_launch(
    request: Request,
    service: LtiServer = Depends(get_lti_service),
    jwt_service: JwtService = Depends(get_jwt_service),
):
    form_data = await request.form()

    user_id = int(form_data.get("user_id"))
    username = form_data.get("ext_user_username", str(user_id))
    full_name = form_data.get("lis_person_name_full", f"User {user_id}")
    roles = form_data.get("roles", "Student")
    # print("=== LTI LAUNCH ===")
    # for key, value in form_data.items():
    #     print(f"{key}: {value}")
    user = service.upsert_user(user_id, username, full_name, roles)
    token = jwt_service.create_token(user.id)
    # print(f"TOKEN: {token}")
    # print(f"id: {user_id}, name: {username}, fullname: {full_name}, roles: {roles}")
    return RedirectResponse(url=f"http://localhost/?token={token}", status_code=303)
