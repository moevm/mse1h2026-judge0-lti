import time

import pytest

pytestmark = pytest.mark.integration
@pytest.mark.asyncio
async def test_login_success(client, create_test_user):
    """Успешный вход"""
    create_test_user(username="logintest", password="correctpass")

    response = await client.post(
        "/api/auth/login", json={"username": "logintest", "password": "correctpass"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"] is not None
    assert "refresh_token" in response.cookies
    assert response.cookies["refresh_token"] is not None


@pytest.mark.asyncio
async def test_login_wrong_password(client, create_test_user):
    """Неверный пароль"""
    create_test_user(username="wrongpassuser", password="correctpass")

    response = await client.post(
        "/api/auth/login",
        json={"username": "wrongpassuser", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Неверный логин или пароль"


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Несуществующий пользователь"""
    response = await client.post(
        "/api/auth/login", json={"username": "nonexistent", "password": "anypass"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Неверный логин или пароль"


@pytest.mark.asyncio
async def test_refresh_success(client, create_test_user):
    """Успешное обновление токена"""
    create_test_user(username="refreshuser", password="correctpass")

    login_resp = await client.post(
        "/api/auth/login",
        json={"username": "refreshuser", "password": "correctpass"},
    )
    refresh_token = login_resp.cookies["refresh_token"]
    time.sleep(1)

    refresh_resp = await client.post(
        "/api/auth/refresh", cookies={"refresh_token": refresh_token}
    )

    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json()

    new_refresh = refresh_resp.cookies.get("refresh_token")
    assert new_refresh is not None
    assert new_refresh != refresh_token


@pytest.mark.asyncio
async def test_refresh_no_token(client):
    """Обновление без токена"""
    response = await client.post("/api/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "No refresh token"


@pytest.mark.asyncio
async def test_refresh_invalid_token(client):
    """Невалидный токен"""
    response = await client.post(
        "/api/auth/refresh", cookies={"refresh_token": "invalid_token"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


@pytest.mark.asyncio
async def test_logout_success(client, create_test_user):
    """Успешный выход"""
    create_test_user(username="logoutuser", password="correctpass")

    login_resp = await client.post(
        "/api/auth/login",
        json={"username": "logoutuser", "password": "correctpass"},
    )
    refresh_token = login_resp.cookies["refresh_token"]

    logout_resp = await client.post(
        "/api/auth/logout", cookies={"refresh_token": refresh_token}
    )

    assert logout_resp.status_code == 200
    assert logout_resp.json()["ok"] is True

    refresh_resp = await client.post(
        "/api/auth/refresh", cookies={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 401


@pytest.mark.asyncio
async def test_logout_without_token(client):
    """Выход без токена"""
    response = await client.post("/api/auth/logout")

    assert response.status_code == 200
    assert response.json()["ok"] is True


@pytest.mark.asyncio
async def test_session_success(client, create_test_user):
    """Успешное получение сессии"""
    create_test_user(username="sessionuser", password="correctpass")

    login_resp = await client.post(
        "/api/auth/login",
        json={"username": "sessionuser", "password": "correctpass"},
    )
    refresh_token = login_resp.cookies["refresh_token"]

    session_resp = await client.get(
        "/api/auth/session", cookies={"refresh_token": refresh_token}
    )

    assert session_resp.status_code == 200
    assert "access_token" in session_resp.json()


@pytest.mark.asyncio
async def test_session_no_token(client):
    """Сессия без токена"""
    response = await client.get("/api/auth/session")

    assert response.status_code == 401
    assert response.json()["detail"] == "No refresh token"