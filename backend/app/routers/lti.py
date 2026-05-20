from fastapi import APIRouter, Request, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from app.services.lti import LtiService, get_lti_service
from app.services.jwt import JwtService, get_jwt_service
from app.services.auth import AuthService, get_auth_service

from app.services.lti13.jwt_utils import get_jwks
import secrets
from urllib.parse import urlencode
from fastapi.responses import RedirectResponse, JSONResponse
from urllib.parse import urlencode, urlparse, parse_qs
import json

router = APIRouter(prefix="/lti", tags=["lti"])


@router.post("/launch", summary="LTI Launch Endpoint")
async def lti_launch(
    request: Request,
    lti_service: LtiService = Depends(get_lti_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    form_data = await request.form()

    user_id = int(form_data.get("user_id"))
    module_id = int(form_data.get("custom_module_id"))
    username = form_data.get("ext_user_username", str(user_id))
    full_name = form_data.get("lis_person_name_full", f"User {user_id}")
    roles = form_data.get("roles", "Student")
    # print("=== LTI LAUNCH ===")
    # for key, value in form_data.items():
    #     print(f"{key}: {value}")
    user = lti_service.upsert_user(user_id, username, full_name, roles)
    access_token, refresh_token = auth_service.issue_lti_session(user)
    response = RedirectResponse(url=f"http://localhost?lti=1&module_id={module_id}", status_code=303)
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


@router.get("/jwks")
async def jwks_endpoint():
    return JSONResponse(content=get_jwks())


@router.api_route("/login", methods=["GET", "POST"])
async def lti13_login(request: Request):
    if request.method == "POST":
        params = await request.form()
    else:
        params = request.query_params

    iss = params.get("iss")
    target_link_uri = params.get("target_link_uri")
    login_hint = params.get("login_hint")
    client_id = params.get("client_id")
    lti_message_hint = params.get("lti_message_hint")

    moodle_auth_url = f"{iss}/mod/lti/auth.php"

    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)

    auth_params = {
        "scope": "openid",
        "response_type": "id_token",
        "client_id": client_id,
        "redirect_uri": target_link_uri,
        "login_hint": login_hint,
        "state": state,
        "nonce": nonce,
        "response_mode": "form_post",
    }

    if lti_message_hint:
        auth_params["lti_message_hint"] = lti_message_hint

    redirect_url = f"{moodle_auth_url}?{urlencode(auth_params)}"

    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/launch13")
async def lti13_launch(
    request: Request,
    lti_service: LtiService = Depends(get_lti_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    form_data = await request.form()
    id_token = form_data.get("id_token")
    state = form_data.get("state")

    print(f"Received id_token: {id_token[:100] if id_token else 'None'}...")

    if not id_token:
        return JSONResponse({"error": "id_token not found"}, status_code=400)

    import jwt
    import base64

    try:
        parts = id_token.split('.')
        if len(parts) != 3:
            return JSONResponse({"error": "Invalid id_token format"}, status_code=400)

        payload_b64 = parts[1]
        payload_b64 += '=' * (4 - len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64)
        decoded = json.loads(payload_json)

        print(f"Decoded payload: {decoded}")

    except Exception as e:
        print(f"Error decoding id_token: {e}")
        return JSONResponse({"error": f"Failed to decode id_token: {str(e)}"}, status_code=400)

    user_id = decoded.get("sub")
    custom_params = decoded.get("https://purl.imsglobal.org/spec/lti/claim/custom", {})
    module_id = custom_params.get("module_id") or decoded.get("custom_module_id")

    if not module_id:
        module_id = 1
        print("WARNING: module_id not found, using default 1")

    username = decoded.get("given_name", str(user_id))
    full_name = decoded.get("name", f"User {user_id}")
    roles_claim = decoded.get("https://purl.imsglobal.org/spec/lti/claim/roles", ["Student"])
    roles = roles_claim[0] if isinstance(roles_claim, list) and roles_claim else "Student"

    user = lti_service.upsert_user(int(user_id), username, full_name, roles)
    access_token, refresh_token = auth_service.issue_lti_session(user)

    response = RedirectResponse(
        url=f"http://localhost?lti=1&module_id={module_id}",
        status_code=303
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return response
