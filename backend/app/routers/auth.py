from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.params import Depends

from app.schemas.auth import AuthResponse, AuthRequest
from app.services.jwt import JwtService, get_jwt_service
from app.services.auth import InvalidCredentialsException, get_auth_service, AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Войти по логину и паролю",
)
async def login(
    body: AuthRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    try:
        access_token, refresh_token = service.login(body)
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль",
        )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return AuthResponse(
        access_token=access_token,
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get("refresh_token")
    print("OLD:", refresh_token)

    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        access_token, new_refresh_token = service.refresh(refresh_token)
        print("NEW:", new_refresh_token)
    except InvalidCredentialsException:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return AuthResponse(access_token=access_token)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        service.logout(refresh_token)
    response.delete_cookie("refresh_token")
    return {"ok": True}

@router.get("/session")
def session(request: Request, service: AuthService = Depends(get_auth_service)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        user = service.get_user_from_refresh(refresh_token)
    except InvalidCredentialsException:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"access_token": service.issue_access_token(user)}
