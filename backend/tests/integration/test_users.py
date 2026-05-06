import pytest
pytestmark = pytest.mark.integration
class TestGetAllUsers:
    """Тесты GET /api/users/"""

    @pytest.mark.asyncio
    async def test_get_all_users_success(self, client, create_test_user):
        """Успешное получение списка пользователей"""
        create_test_user(username="user1", full_name="User One")
        create_test_user(username="user2", full_name="User Two")

        response = await client.get("/api/users/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["username"] == "user1"
        assert data[1]["username"] == "user2"

    @pytest.mark.asyncio
    async def test_get_all_users_empty(self, client):
        """Получение списка когда нет пользователей"""
        response = await client.get("/api/users/")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_all_users_with_search(self, client, create_test_user):
        """Фильтрация пользователей по поиску"""
        create_test_user(username="john_doe", full_name="John Doe")
        create_test_user(username="jane_doe", full_name="Jane Doe")
        create_test_user(username="bob_smith", full_name="Bob Smith")

        response = await client.get("/api/users/?search=doe")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        usernames = [u["username"] for u in data]
        assert "john_doe" in usernames
        assert "jane_doe" in usernames

    @pytest.mark.asyncio
    async def test_get_all_users_exclude_deleted(self, client, create_test_user):
        """Исключение удаленных пользователей"""
        create_test_user(username="active_user")
        create_test_user(username="deleted_user", deleted=True)

        response = await client.get("/api/users/?include_deleted=false")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["username"] == "active_user"

    @pytest.mark.asyncio
    async def test_get_all_users_include_deleted(self, client, create_test_user):
        """Включение удаленных пользователей"""
        create_test_user(username="active_user")
        create_test_user(username="deleted_user", deleted=True)

        response = await client.get("/api/users/?include_deleted=true")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestGetUser:
    """Тесты GET /api/users/{user_id}"""

    @pytest.mark.asyncio
    async def test_get_user_success(self, client, create_test_user):
        """Успешное получение пользователя по ID"""
        user = create_test_user(username="target_user", full_name="Target User")

        response = await client.get(f"/api/users/{user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["username"] == "target_user"
        assert data["full_name"] == "Target User"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client):
        """Получение несуществующего пользователя"""
        response = await client.get("/api/users/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Пользователь не найден"


class TestUpdateUser:
    """Тесты PATCH /api/users/{user_id}"""

    @pytest.mark.asyncio
    async def test_update_user_success(self, client, create_test_user):
        """Успешное обновление пользователя"""
        user = create_test_user(full_name="Original Name", role="student")

        response = await client.patch(
            f"/api/users/{user.id}",
            json={"full_name": "Updated Name", "role": "teacher"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["role"] == "teacher"

    @pytest.mark.asyncio
    async def test_update_user_partial(self, client, create_test_user):
        """Частичное обновление пользователя"""
        user = create_test_user(full_name="Original Name", role="student")

        response = await client.patch(
            f"/api/users/{user.id}", json={"full_name": "Only Name Updated"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Only Name Updated"
        assert data["role"] == "student"

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, client):
        """Обновление несуществующего пользователя"""
        response = await client.patch(
            "/api/users/999", json={"full_name": "New Name"}
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Пользователь не найден"


class TestDeleteUser:
    """Тесты DELETE /api/users/{user_id}"""

    @pytest.mark.asyncio
    async def test_delete_user_success(self, client, create_test_user):
        """Успешное мягкое удаление пользователя"""
        user = create_test_user(username="to_delete")

        response = await client.delete(f"/api/users/{user.id}")

        assert response.status_code == 204

        get_response = await client.get("/api/users/")
        data = get_response.json()
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, client):
        """Удаление несуществующего пользователя"""
        response = await client.delete("/api/users/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Пользователь не найден"


class TestFullUserFlow:
    """Полный цикл работы с пользователями"""
    @pytest.mark.asyncio
    async def test_full_user_flow(self, client, create_test_user):
        user = create_test_user(
            username="flow_user", full_name="Flow User", role="student"
        )

        get_response = await client.get(f"/api/users/{user.id}")
        assert get_response.status_code == 200
        assert get_response.json()["full_name"] == "Flow User"

        update_response = await client.patch(
            f"/api/users/{user.id}",
            json={"full_name": "Updated Flow User", "role": "teacher"},
        )
        assert update_response.status_code == 200
        assert update_response.json()["full_name"] == "Updated Flow User"
        assert update_response.json()["role"] == "teacher"

        list_response = await client.get("/api/users/")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1

        delete_response = await client.delete(f"/api/users/{user.id}")
        assert delete_response.status_code == 204

        # После мягкого удаления пользователь не отображается в общем списке
        list_after = await client.get("/api/users/?include_deleted=false")
        assert len(list_after.json()) == 0

        # Но админ может получить его по ID (прямое обращение)
        get_deleted = await client.get(f"/api/users/{user.id}")
        assert get_deleted.status_code == 200
        assert get_deleted.json()["full_name"] == "Updated Flow User"
        assert get_deleted.json()["deleted_at"] is not None  # есть отметка об удалении

        # Если указать include_deleted=true, то он появится в списке
        list_with_deleted = await client.get("/api/users/?include_deleted=true")
        assert len(list_with_deleted.json()) == 1
