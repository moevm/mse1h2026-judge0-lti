import pytest
from typing import AsyncGenerator
from fastapi import FastAPI, APIRouter
from httpx import AsyncClient, ASGITransport

from app.routers import auth
from app.services.auth import AuthService
from tests.mocks import (
    MockUserRepository,
    MockRefreshTokenRepository,
    MockJwtService,
    MockUser,
    mock_hash_password,
)


@pytest.fixture
def mock_user_repo():
    return MockUserRepository()


@pytest.fixture
def mock_token_repo():
    return MockRefreshTokenRepository()


@pytest.fixture
def mock_jwt_service():
    return MockJwtService()


@pytest.fixture
def auth_service(mock_user_repo, mock_token_repo, mock_jwt_service):
    """Реальный AuthService с мок-репозиториями"""
    return AuthService(
        user_repo=mock_user_repo,
        token_repo=mock_token_repo,
        jwt_service=mock_jwt_service,
    )


@pytest.fixture
def app_with_auth(auth_service):
    """Приложение с auth роутерами и моками"""
    app = FastAPI()
    api_router = APIRouter(prefix="/api")
    api_router.include_router(auth.router)
    app.include_router(api_router)

    def get_mock_auth_service():
        return auth_service

    app.dependency_overrides[auth.get_auth_service] = get_mock_auth_service
    return app


@pytest.fixture
async def client(app_with_auth) -> AsyncGenerator:
    """HTTP клиент для тестов auth"""
    transport = ASGITransport(app=app_with_auth)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def create_test_user(mock_user_repo):
    """Создание тестового пользователя в мок-репозитории"""
    def _create_user(
        username: str = "testuser", password: str = "correctpass", role: str = "student"
    ):
        user = MockUser(
            username=username,
            password_hash=mock_hash_password(password),
            full_name=f"{username} Full Name",
            role=role,
        )
        mock_user_repo.add(user)
        return user
    return _create_user