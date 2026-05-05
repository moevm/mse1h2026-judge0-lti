class MockUser:
    def __init__(
        self,
        username: str,
        password_hash: str,
        full_name: str = "Test User",
        role: str = "student",
    ):
        self.id = None
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name
        self.role = type("Role", (), {"value": role})()
        self.deleted_at = None


class MockRefreshToken:
    def __init__(self, user_id: int, token_hash: str, expires_at):
        self.id = None
        self.user_id = user_id
        self.token_hash = token_hash
        self.expires_at = expires_at
        self.revoked = False