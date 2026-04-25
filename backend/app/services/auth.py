from datetime import datetime, timezone

from fastapi import Depends

from app.schemas.auth import AuthRequest
from app.services.jwt import JwtService, get_jwt_service
from app.repositories.user import UserRepository, get_user_repository
from app.database.models import RefreshToken, User
from app.repositories.refresh_token import (
    RefreshTokenRepository,
    get_refresh_token_repository,
)
from app.core.security import verify_password
from app.core.security import hash_token


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
        if not user or not verify_password(body.password, user.password_hash):
            raise InvalidCredentialsException

        access_token = self.issue_access_token(user)

        refresh_token, expires_at = self.jwt_service.create_refresh_token(
            user_id=user.id
        )
        token_hash = hash_token(refresh_token)

        db_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.token_repo.add(db_token)

        return access_token, refresh_token

    def refresh(self, refresh_token: str):
        token_hash = hash_token(refresh_token)
        db_token = self.token_repo.get_by_hash(token_hash)
        if (
            not db_token
            or db_token.revoked
            or db_token.expires_at < datetime.now(timezone.utc)
        ):
            raise InvalidCredentialsException
        user = self.user_repo.get_by_id(db_token.user_id)
        new_access = self.issue_access_token(user)
        new_refresh, expires_at = self.jwt_service.create_refresh_token(
            user_id=user.id,
        )
        db_token.revoked = True
        self.token_repo.add(
            RefreshToken(
                user_id=user.id,
                token_hash=hash_token(new_refresh),
                expires_at=expires_at,
            )
        )
        return new_access, new_refresh

    def logout(self, refresh_token: str):
        token_hash = hash_token(refresh_token)
        db_token = self.token_repo.get_by_hash(token_hash)
        if not db_token:
            return
        self.token_repo.revoke(db_token)

    def issue_lti_session(self, user):
        self.token_repo.delete_all_by_user(user.id)
        access = self.issue_access_token(user)
        refresh, expires_at = self.jwt_service.create_refresh_token(user.id)
        self.token_repo.add(
            RefreshToken(
                user_id=user.id,
                token_hash=hash_token(refresh),
                expires_at=expires_at,
            )
        )
        return access, refresh

    def issue_access_token(self, user: User):
        access = self.jwt_service.create_access_token(
            user_id=user.id,
            role=user.role.value,
        )
        return access

    def get_user_from_refresh(self, refresh_token: str) -> User:
        token_hash = hash_token(refresh_token)
        db_token = self.token_repo.get_by_hash(token_hash)
        if not db_token or db_token.revoked:
            raise InvalidCredentialsException
        return self.user_repo.get_by_id(db_token.user_id)


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
