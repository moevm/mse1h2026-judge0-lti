from datetime import datetime, timedelta, timezone
import hashlib

from fastapi import Depends

from app.schemas.auth import AuthRequest
from app.services.jwt import JwtService, get_jwt_service
from app.repositories.user import UserRepository, get_user_repository
from app.database.models import RefreshToken
from app.repositories.refresh_token import (
    RefreshTokenRepository,
    get_refresh_token_repository,
)
from app.security import verify_password


class InvalidCredentialsException(Exception):
    pass


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: RefreshTokenRepository,
        jwt_service: JwtService,
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.jwt_service = jwt_service

    def login(self, body: AuthRequest):
        user = self.user_repo.get_by_username(body.username)

        if not user:
            raise InvalidCredentialsException
        if not verify_password(body.password, user.password_hash):
            raise InvalidCredentialsException

        access_token = self.jwt_service.create_access_token(
            user_id=user.id,
            role=user.role.value,
        )

        refresh_token, expires_at = self.jwt_service.create_refresh_token(
            user_id=user.id
        )
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        db_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.token_repo.add(db_token)
        self.token_repo.flush()

        return access_token, refresh_token


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    token_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
    jwt_service: JwtService = Depends(get_jwt_service),
) -> AuthService:
    return AuthService(
        user_repo=user_repo,
        token_repo=token_repo,
        jwt_service=jwt_service,
    )
