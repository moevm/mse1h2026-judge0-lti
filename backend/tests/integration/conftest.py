import os
import pytest

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
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

from sqlalchemy.pool import NullPool
@pytest_asyncio.fixture(scope="session")
async def engine(postgres_container):
    url = postgres_container.get_connection_url()
    url = url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    engine = create_async_engine(url, poolclass=NullPool, future=True)

    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        from app.database.models import Language
        for lang_name in ["python", "javascript", "java", "cpp", "c", "go", "rust"]:
            result = await session.execute(
                select(Language).where(Language.language == lang_name)
            )
            if not result.scalars().first():
                session.add(Language(language=lang_name))
        await session.commit()

    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(scope="session")
async def session_factory(engine):
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
    )

@pytest_asyncio.fixture(autouse=True)
async def override_db(session_factory):
    async def override_get_db():
        async with session_factory() as session:
            yield session
    main_app.dependency_overrides[session_generator] = override_get_db
    yield
    main_app.dependency_overrides.clear()

@pytest_asyncio.fixture(autouse=True)
async def truncate_tables(engine):
    yield
    async with engine.begin() as conn:
        await conn.execute(text(
            "TRUNCATE TABLE attempts, solutions, module_sessions, "
            "refresh_tokens, tasks_languages, module_tasks_order, task_tests, tasks, "
            "modules, users RESTART IDENTITY CASCADE"
        ))
@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=main_app), base_url="http://test"
    ) as client:
        yield client

@pytest_asyncio.fixture(autouse=True)
async def mock_judge_service():
    from unittest.mock import AsyncMock, MagicMock
    from app.services.judge import get_judge_service

    mock_service = MagicMock()
    mock_service.execute_code = AsyncMock(
        return_value={
            "stdout": "mocked output",
            "stderr": None,
            "compile_output": None,
            "status": {"id": 3, "description": "Accepted"},
        }
    )
    async def _mock():
        return mock_service
    main_app.dependency_overrides[get_judge_service] = _mock
    yield
    main_app.dependency_overrides.pop(get_judge_service, None)

@pytest_asyncio.fixture(autouse=True)
async def mock_admin_auth():
    from app.core.dependencies import get_current_admin
    from app.database.models import User, UserTypeEnum

    async def _mock():
        admin = User()
        admin.id = 1
        admin.username = "admin"
        admin.full_name = "Admin User"
        admin.role = UserTypeEnum.admin
        return admin
    main_app.dependency_overrides[get_current_admin] = _mock
    yield
    main_app.dependency_overrides.pop(get_current_admin, None)

@pytest_asyncio.fixture
async def create_test_user(session_factory):
    from app.database.models import User, UserTypeEnum
    from app.core.security import hash_password
    from datetime import datetime, timezone

    async def _create_user(
        username="testuser",
        password="correctpass",
        full_name=None,
        role="student",
        deleted=False,
    ):
        async with session_factory() as session:
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
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    return _create_user

@pytest_asyncio.fixture
async def create_test_task(session_factory):
    from app.database.models import Task, Language

    async def _create_task(
        title="Test Task",
        description="Task Description",
        timeout=10,
        language_names=None,
    ):
        if language_names is None:
            language_names = ["python", "javascript"]
        async with session_factory() as session:
            task = Task(
                title=title,
                description=description,
                timeout=timeout,
            )
            session.add(task)
            for lang_name in language_names:
                result = await session.execute(
                    select(Language).where(Language.language == lang_name)
                )
                lang = result.scalars().first()
                if lang:
                    task.languages.append(lang)
            await session.commit()
            await session.refresh(task)
            return task
    return _create_task

@pytest_asyncio.fixture
async def create_test_module(session_factory):
    from app.database.models import Module

    async def _create_module(
        title="Test Module",
        description="Module Description",
    ):
        async with session_factory() as session:
            module = Module(
                title=title,
                description=description,
            )
            session.add(module)
            await session.commit()
            await session.refresh(module)
            return module
    return _create_module

@pytest_asyncio.fixture
async def create_test_test(session_factory):
    from app.database.models import TaskTest

    async def _create_test(task_id, title="Test Case", stdin="", stdout="expected"):
        async with session_factory() as session:
            test = TaskTest()
            test.task_id = task_id
            test.title = title
            test.stdin = stdin
            test.stdout = stdout
            session.add(test)
            await session.commit()
            await session.refresh(test)
            return test
    return _create_test

@pytest_asyncio.fixture
async def create_test_tasks(create_test_task):
    async def _create_tasks(count=3):
        tasks = []
        for i in range(1, count + 1):
            tasks.append(await create_test_task(title=f"Task {i}"))
        return tasks
    return _create_tasks

@pytest_asyncio.fixture
async def auth_client(client, create_test_user):
    from app.services.jwt import JwtService

    user = await create_test_user(
        username="analytics_user",
        password="testpass",
        role="admin",
    )
    jwt_service = JwtService(mock_get_settings())
    token = jwt_service.create_access_token(user_id=user.id, role=models.UserTypeEnum.admin)
    client.headers.update({"Authorization": f"Bearer {token}"})
    class _User:
        id = user.id
        username = user.username
    return client, _User()