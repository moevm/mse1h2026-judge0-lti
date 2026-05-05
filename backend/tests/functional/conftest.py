import os
import pytest
from typing import AsyncGenerator
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.services.jwt import JwtService

os.environ["MOCK_JUDGE0"] = os.getenv("MOCK_JUDGE0", "false")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "test_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "test_pass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "test_db")
JUDGE0_URL = os.getenv("JUDGE0_URL", "http://localhost:2358")

DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
from app.core.config import Settings

def mock_get_settings():
    return Settings(
        postgres_user=POSTGRES_USER,
        postgres_password=POSTGRES_PASSWORD,
        postgres_db=POSTGRES_DB,
        postgres_host=POSTGRES_HOST,
        postgres_port=int(POSTGRES_PORT),
        mock_judge0=os.getenv("MOCK_JUDGE0", "false"),
        judge0_url=JUDGE0_URL,
        jwt_secret_key=os.getenv("JWT_SECRET_KEY", "test_secret_key_12345"),
        access_token_expire_minutes=30,
        refresh_token_expire_days=7,
        admin_username="admin",
        admin_password="adminpass",
    )


import app.core.config

app.core.config.get_settings = mock_get_settings

from app.main import app as main_app
from app.database.database import session_generator
from app.database import models
from app.core.security import hash_password, hash_token


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(DB_URL)
    models.Base.metadata.create_all(bind=engine)

    from app.database.models import Language

    Session = sessionmaker(bind=engine)
    session = Session()

    default_languages = [
        "Python (3.8.1)",
        "JavaScript (Node.js 12.14.0)",
        "Java (OpenJDK 13.0.1)",
        "C (Clang 7.0.1)",
        "C++ (Clang 7.0.1)",
        "Go (1.13)",
        "Rust (1.40)",
    ]
    for lang_name in default_languages:
        lang = session.query(Language).filter(Language.language == lang_name).first()
        if not lang:
            session.add(Language(language=lang_name))

    session.commit()
    session.close()

    yield engine
    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    def override_get_db():
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    main_app.dependency_overrides[session_generator] = override_get_db

    yield session

    from app.database.models import Base

    table_names = [
        "module_tasks_order",
        "refresh_tokens",
        "task_tests",
        "tasks_languages",
        "tasks",
        "modules",
        "users",
    ]
    for table_name in table_names:
        session.execute(text(f'TRUNCATE TABLE "{table_name}" CASCADE'))
    session.commit()

    transaction.rollback()
    connection.close()
    main_app.dependency_overrides.clear()


@pytest.fixture
async def client(db_session) -> AsyncGenerator:
    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def student_user(db_session):
    from app.database.models import User, UserTypeEnum, RefreshToken

    user = User()
    user.username = "student"
    user.password_hash = hash_password("studentpass")
    user.full_name = "Test Student"
    user.role = UserTypeEnum.student
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)

    db_session.add(user)
    db_session.flush()

    jwt_service = JwtService(mock_get_settings())
    refresh_token, expires_at = jwt_service.create_refresh_token(user_id=user.id)

    refresh_token_obj = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=expires_at,
        revoked=False,
    )
    db_session.add(refresh_token_obj)
    db_session.commit()
    db_session.refresh(user)

    return user, refresh_token


@pytest.fixture
async def student_auth(client, student_user):
    """Авторизованный студент через refresh token в cookies"""
    user, refresh_token = student_user

    refresh_response = await client.post(
        "/api/auth/refresh", cookies={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    access_token = refresh_response.json()["access_token"]

    client.headers["Authorization"] = f"Bearer {access_token}"
    client.cookies.set("refresh_token", refresh_token)

    return client, user


@pytest.fixture
def create_admin_user(db_session):
    """Создаем админа в БД"""
    from app.database.models import User, UserTypeEnum

    admin = db_session.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User()
        admin.username = "admin"
        admin.password_hash = hash_password("adminpass")
        admin.full_name = "Admin User"
        admin.role = UserTypeEnum.admin
        admin.created_at = datetime.now(timezone.utc)
        admin.updated_at = datetime.now(timezone.utc)
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
    return admin


@pytest.fixture
async def admin_auth(client, create_admin_user):
    """Авторизованный админ"""
    login_response = await client.post(
        "/api/auth/login", json={"username": "admin", "password": "adminpass"}
    )
    assert login_response.status_code == 200, "Admin user must exist in database"
    access_token = login_response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {access_token}"
    return client


@pytest.fixture
async def create_task_via_api(admin_auth):
    """Создание задачи через API"""

    async def _create_task(title: str, description: str, timeout: int, languages: list):
        response = await admin_auth.post(
            "/api/tasks/",
            json={
                "title": title,
                "description": description,
                "timeout": timeout,
                "languages": languages,
            },
        )
        assert response.status_code == 200
        return response.json()

    return _create_task


@pytest.fixture
async def create_module_via_api(admin_auth):
    """Создание модуля через API"""

    async def _create_module(title: str, description: str):
        response = await admin_auth.post(
            "/api/modules/", json={"title": title, "description": description}
        )
        assert response.status_code == 200
        return response.json()

    return _create_module


@pytest.fixture
async def add_task_to_module_via_api(admin_auth):
    """Добавление задачи в модуль через API"""

    async def _add_task(module_id: int, task_ids: list):
        response = await admin_auth.post(
            f"/api/modules/{module_id}/tasks", json={"task_ids": task_ids}
        )
        assert response.status_code == 200
        return response.json()

    return _add_task


@pytest.fixture
async def create_test_via_api(admin_auth):
    """Создание теста для задачи через API"""

    async def _create_test(task_id: int, title: str, stdin: str, stdout: str):
        response = await admin_auth.post(
            f"/api/tasks/{task_id}/tests",
            json={
                "title": title,
                "stdin": stdin,
                "stdout": stdout,
            },
        )
        assert response.status_code == 200
        return response.json()

    return _create_test
