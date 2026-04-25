from fastapi import APIRouter, HTTPException, Response
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
