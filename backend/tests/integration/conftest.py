import os
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

os.environ["JWT_SECRET_KEY"] = "test_secret_key_12345"
os.environ["MOCK_JUDGE0"] = "true"
os.environ["POSTGRES_USER"] = "test_user"
os.environ["POSTGRES_PASSWORD"] = "test_pass"
os.environ["POSTGRES_DB"] = "test_db"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5433"

from app.core.config import Settings


def mock_get_settings():
    return Settings(
        postgres_user=os.environ["POSTGRES_USER"],
        postgres_password=os.environ["POSTGRES_PASSWORD"],
        postgres_db=os.environ["POSTGRES_DB"],
        postgres_host=os.environ["POSTGRES_HOST"],
        postgres_port=int(os.environ["POSTGRES_PORT"]),
        mock_judge0=os.environ["MOCK_JUDGE0"],
        judge0_url=os.getenv("JUDGE0_URL", "http://test_judge0:2358"),
        jwt_secret_key=os.environ["JWT_SECRET_KEY"],
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


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:17-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def engine(postgres_container):
    url = postgres_container.get_connection_url()
    engine = create_engine(url)
    models.Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    default_languages = ["python", "javascript", "java", "cpp", "c", "go", "rust"]
    for lang_name in default_languages:
        from app.database.models import Language
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
            session.flush()
        except Exception:
            session.rollback()
            raise

    main_app.dependency_overrides[session_generator] = override_get_db

    yield session

    transaction.rollback()
    connection.close()
    main_app.dependency_overrides.clear()
@pytest.fixture
async def client(db_session) -> AsyncGenerator:
    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.fixture(autouse=True)
def mock_judge_service():
    from app.services.judge import get_judge_service
    from unittest.mock import AsyncMock, MagicMock

    mock_service = MagicMock()
    mock_service.execute_code = AsyncMock(
        return_value={
            "stdout": "mocked output",
            "stderr": None,
            "compile_output": None,
            "status": {"id": 3, "description": "Accepted"},
        }
    )

    async def mock_get_judge_service():
        return mock_service

    main_app.dependency_overrides[get_judge_service] = mock_get_judge_service
    yield
    main_app.dependency_overrides.pop(get_judge_service, None)


@pytest.fixture(autouse=True)
def mock_admin_auth():
    from app.core.dependencies import get_current_admin
    from app.database.models import User, UserTypeEnum

    async def mock_get_current_admin():
        admin = User()
        admin.id = 1
        admin.username = "admin"
        admin.full_name = "Admin User"
        admin.role = UserTypeEnum.admin
        return admin

    main_app.dependency_overrides[get_current_admin] = mock_get_current_admin
    yield
    main_app.dependency_overrides.pop(get_current_admin, None)


@pytest.fixture
async def auth_client(client, create_test_user):
    from app.services.jwt import JwtService

    user = create_test_user(
        username="analytics_user", password="testpass", role="admin"
    )

    user_id = user.id
    name = user.username

    jwt_service = JwtService(mock_get_settings())
    access_token = jwt_service.create_access_token(user_id=user_id, role="admin")

    client.headers["Authorization"] = f"Bearer {access_token}"

    class _User:
        id = user_id
        username = name

    return client, _User()


@pytest.fixture
def create_test_user(db_session):
    from app.database.models import User, UserTypeEnum
    from app.core.security import hash_password
    from datetime import datetime, timezone

    def _create_user(
        username: str = "testuser",
        password: str = "correctpass",
        full_name: str = None,
        role: str = "student",
        deleted: bool = False,
    ):
        user = User()
        user.username = username
        user.password_hash = hash_password(password)
        user.full_name = full_name or f"{username} Full Name"

        if role == "admin":
            user.role = UserTypeEnum.admin
        elif role == "teacher":
            user.role = UserTypeEnum.teacher
        else:
            user.role = UserTypeEnum.student

        if deleted:
            user.deleted_at = datetime.now(timezone.utc)

        db_session.add(user)
        db_session.flush()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def create_test_task(db_session):
    from app.database.models import Task, Language

    def _create_task(
        title: str = "Test Task",
        description: str = "Task Description",
        timeout: int = 10,
        language_names: list = None,
    ):
        if language_names is None:
            language_names = ["python", "javascript"]

        task = Task()
        task.title = title
        task.description = description
        task.timeout = timeout

        db_session.add(task)
        db_session.flush()

        for lang_name in language_names:
            lang = (
                db_session.query(Language)
                .filter(Language.language == lang_name)
                .first()
            )
            if not lang:
                lang = Language(language=lang_name)
                db_session.add(lang)
                db_session.flush()
            task.languages.append(lang)

        db_session.flush()
        db_session.refresh(task)
        return task

    return _create_task


@pytest.fixture
def create_test_test(db_session):
    from app.database.models import TaskTest

    def _create_test(
        task_id: int,
        title: str = "Test Case",
        stdin: str = "",
        stdout: str = "expected output",
    ):
        test = TaskTest()
        test.task_id = task_id
        test.title = title
        test.stdin = stdin
        test.stdout = stdout

        db_session.add(test)
        db_session.flush()
        db_session.refresh(test)
        return test

    return _create_test


@pytest.fixture
def create_test_tasks(db_session, create_test_task):
    def _create_tasks(count: int = 3):
        tasks = []
        for i in range(1, count + 1):
            task = create_test_task(title=f"Task {i}")
            tasks.append(task)
        return tasks
    return _create_tasks


@pytest.fixture
def create_test_module(db_session):
    from app.database.models import Module

    def _create_module(
        title: str = "Test Module",
        description: str = "Module Description",
    ):
        module = Module()
        module.title = title
        module.description = description

        db_session.add(module)
        db_session.flush()
        db_session.refresh(module)
        return module

    return _create_module