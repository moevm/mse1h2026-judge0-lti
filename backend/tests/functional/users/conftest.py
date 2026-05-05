import pytest
from typing import AsyncGenerator
from fastapi import FastAPI, APIRouter
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone

from app.routers import users as users_router
from app.services.users import UserService
from tests.mocks import (
    MockUserRepository,
    MockJwtService,
)
from app.database.models import User, UserTypeEnum

@pytest.fixture
def mock_user_repo():
    repo = MockUserRepository()
    repo.clear()
    return repo


@pytest.fixture
def mock_jwt_service():
    return MockJwtService()


@pytest.fixture
def user_service(mock_user_repo):
    return UserService(repo=mock_user_repo)


@pytest.fixture
def app_with_users(user_service, mock_jwt_service):
    app = FastAPI()
    api_router = APIRouter(prefix="/api")
    api_router.include_router(users_router.router)
    app.include_router(api_router)

    def get_mock_user_service():
        return user_service

    def get_mock_jwt_service():
        return mock_jwt_service

    app.dependency_overrides[users_router.get_user_service] = get_mock_user_service
    app.dependency_overrides[users_router.get_jwt_service] = get_mock_jwt_service

    from app.core.dependencies import get_current_admin

    async def mock_get_current_admin():
        admin = User()
        admin.id = 1
        admin.username = "admin"
        admin.full_name = "Admin User"
        admin.role = UserTypeEnum.admin
        admin.created_at = datetime.now(timezone.utc)
        admin.updated_at = datetime.now(timezone.utc)
        return admin

    app.dependency_overrides[get_current_admin] = mock_get_current_admin

    from app.core.dependencies import get_current_user_payload

    async def mock_get_current_user_payload():
        return {"user_id": 1, "role": "student"}

    app.dependency_overrides[get_current_user_payload] = mock_get_current_user_payload

    return app


@pytest.fixture
async def users_client(app_with_users) -> AsyncGenerator:
    transport = ASGITransport(app=app_with_users)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def create_test_user(mock_user_repo):
    """Создание тестового пользователя"""

    def _create_user(
        username: str = "testuser",
        full_name: str = "Test User",
        role: str = "student",
        password_hash: str = "hashed_password",
        deleted: bool = False,
    ):
        user = User()
        user.username = username
        user.full_name = full_name
        if role == "admin":
            user.role = UserTypeEnum.admin
        elif role == "teacher":
            user.role = UserTypeEnum.teacher
        else:
            user.role = UserTypeEnum.student

        user.password_hash = password_hash
        user.created_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        user.deleted_at = datetime.now(timezone.utc) if deleted else None

        mock_user_repo.add(user)
        return user

    return _create_user


@pytest.fixture
def auth_header(mock_jwt_service):
    token = mock_jwt_service.create_access_token(user_id=1, role="student")
    return {"Authorization": f"Bearer {token}"}
