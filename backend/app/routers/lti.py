import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.core.config import get_settings
from app.core.exceptions.auth import RefreshTokenMissingException
from app.services.auth import AuthService, get_auth_service
from app.services.lti import LtiService, get_lti_service
from cryptography.hazmat.primitives import serialization
from fastapi.responses import PlainTextResponse
from app.services.lti13.jwt_utils import get_jwks, verify_lti13_token, _load_private_key

router = APIRouter(prefix="/lti", tags=["lti"])
settings = get_settings()

@router.post("/launch", summary="LTI 1.1 Launch")
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

    user = lti_service.upsert_user(user_id, username, full_name, roles)
    access_token, refresh_token = auth_service.issue_lti_session(user)

    response = RedirectResponse(
        url=f"http://localhost?lti=1&module_id={module_id}",
        status_code=303,
    )
    _set_refresh_cookie(response, refresh_token)
    return response



@router.api_route("/login", methods=["GET", "POST"], summary="LTI 1.3 OIDC Login")
async def lti13_login(request: Request):
    params = await request.form() if request.method == "POST" else request.query_params

    iss = params.get("iss")
    target_link_uri = params.get("target_link_uri")
    login_hint = params.get("login_hint")
    client_id = params.get("client_id")
    lti_message_hint = params.get("lti_message_hint")

    auth_params = {
        "scope": "openid",
        "response_type": "id_token",
        "client_id": client_id,
        "redirect_uri": target_link_uri,
        "login_hint": login_hint,
        "state": secrets.token_urlsafe(32),
        "nonce": secrets.token_urlsafe(32),
        "response_mode": "form_post",
    }
    if lti_message_hint:
        auth_params["lti_message_hint"] = lti_message_hint

    moodle_auth_url = f"{iss}/mod/lti/auth.php"
    return RedirectResponse(url=f"{moodle_auth_url}?{urlencode(auth_params)}", status_code=303)


@router.post("/launch13", summary="LTI 1.3 Launch")
async def lti13_launch(
    request: Request,
    lti_service: LtiService = Depends(get_lti_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    form_data = await request.form()
    id_token = form_data.get("id_token")

    if not id_token:
        raise HTTPException(status_code=400, detail="id_token not found")

    decoded = verify_lti13_token(
        id_token=id_token,
        moodle_jwks_url=settings.moodle_jwks_url,
        expected_aud=settings.lti_client_id,
    )

    user_id = int(decoded["sub"])
    full_name = decoded.get("name", f"User {user_id}")
    username = decoded.get("given_name", str(user_id))

    roles_claim = decoded.get("https://purl.imsglobal.org/spec/lti/claim/roles", [])
    roles = roles_claim[0] if roles_claim else "Student"

    custom = decoded.get("https://purl.imsglobal.org/spec/lti/claim/custom", {})
    module_id = custom.get("module_id") or decoded.get("custom_module_id") or 1

    user = lti_service.upsert_user(user_id, username, full_name, roles)
    _, refresh_token = auth_service.issue_lti_session(user)

    response = RedirectResponse(
        url=f"http://localhost?lti=1&module_id={module_id}",
        status_code=303,
    )
    _set_refresh_cookie(response, refresh_token)
    return response

@router.get("/jwks", summary="JWKS endpoint")
async def jwks_endpoint():
    return JSONResponse(content=get_jwks())


@router.get("/public-key", response_class=PlainTextResponse)
async def public_key():
    return _load_private_key().public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()


@router.get("/session", summary="Exchange refresh cookie → access token")
def session(request: Request, auth_service: AuthService = Depends(get_auth_service)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise RefreshTokenMissingException()
    user = auth_service.get_user_from_refresh(refresh_token)

    return {"access_token": auth_service.issue_access_token(user)}

def _set_refresh_cookie(response: RedirectResponse, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False, 
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )