from typing import Callable

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.exceptions.auth import (
    InvalidAccessTokenException,
    InvalidTokenTypeException,
)
from app.core.exceptions.users import UserNotFoundException
from app.services.jwt import JwtService, get_jwt_service
from app.repositories.user import UserRepository, get_user_repository
from app.database.models import User, UserTypeEnum
from app.schemas.auth import TokenUser

bearer = HTTPBearer()


def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    jwt_service: JwtService = Depends(get_jwt_service),
) -> TokenUser:
    try:
        payload = jwt_service.decode_access_token(credentials.credentials)
        if payload.get("type") != "access":
            raise InvalidTokenTypeException()
        return TokenUser(
            user_id=payload["user_id"],
            role=UserTypeEnum(payload["role"]),
        )
    except Exception:
        raise InvalidAccessTokenException()


async def get_current_user(
    payload: dict = Depends(get_current_user_payload),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    user_id = payload.get("user_id")
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundException()
    return user


def get_current_admin(
    payload: TokenUser = Depends(get_current_user_payload),
) -> TokenUser:
    if payload.role != UserTypeEnum.admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return payload


def require_roles(*allowed_roles: UserTypeEnum) -> Callable:
    def dependency(payload: TokenUser = Depends(get_current_user_payload)) -> TokenUser:
        if payload.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return payload
    return dependency