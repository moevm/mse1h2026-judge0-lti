import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ["POSTGRES_USER"] = "test_user"
os.environ["POSTGRES_PASSWORD"] = "test_pass"
os.environ["POSTGRES_DB"] = "test_db"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["JWT_SECRET_KEY"] = "test_secret_key_for_testing_only_12345"
os.environ["MOCK_JUDGE0"] = "true"

import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.core.config import get_settings, Settings
from tests.mocks import create_mock_pwd_context, mock_hash_token

def mock_get_settings():
    return Settings(
        postgres_user=os.environ["POSTGRES_USER"],
        postgres_password=os.environ["POSTGRES_PASSWORD"],
        postgres_db=os.environ["POSTGRES_DB"],
        postgres_host=os.environ["POSTGRES_HOST"],
        postgres_port=int(os.environ["POSTGRES_PORT"]),
        mock_judge0=os.environ["MOCK_JUDGE0"],
        judge0_url="http://test_judge0:2358",
        jwt_secret_key=os.environ["JWT_SECRET_KEY"],
        access_token_expire_minutes=30,
        refresh_token_expire_days=7,
        admin_username="admin",
        admin_password="adminpass",
    )


import app.core.config
app.core.config.get_settings = mock_get_settings


import app.core.security
app.core.security.pwd_context = create_mock_pwd_context()


import app.services.auth as auth_module
auth_module.hash_token = mock_hash_token

@pytest.fixture
def base_app():
    return FastAPI()


@pytest.fixture
async def client(base_app) -> AsyncGenerator:
    transport = ASGITransport(app=base_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client