from app.schemas.auth import AuthRequest, AuthResponse
from app.services.auth import AuthService, get_auth_service
from fastapi import APIRouter, Request, Response
from fastapi.params import Depends

from app.core.exceptions.auth import RefreshTokenMissingException

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
    access_token, refresh_token = await service.login(body)
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


@router.post("/refresh", response_model=AuthResponse, summary="Обновить access токен")
async def refresh(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise RefreshTokenMissingException()
    access_token, new_refresh_token = await service.refresh(refresh_token)
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return AuthResponse(access_token=access_token)


@router.post("/logout", summary="Выход")
async def logout(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await service.logout(refresh_token)
    response.delete_cookie("refresh_token")
    return {"ok": True}


# использовать этот эндпоинт на фронте для получения access токена после редиректа с lti
@router.get("/session", summary="Получить access токен по refresh (после lti)")
async def session(request: Request, service: AuthService = Depends(get_auth_service)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise RefreshTokenMissingException()
    user = await service.get_user_from_refresh(refresh_token)

    return {"access_token": service.issue_access_token(user)}
