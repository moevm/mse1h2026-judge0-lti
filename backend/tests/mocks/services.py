from app.services.jwt import JwtService
from datetime import datetime, timedelta, timezone


class MockJwtService(JwtService):
    def __init__(self):
        self.access_counter = 0
        self.refresh_counter = 0

    def create_access_token(self, user_id: int, role: str):
        self.access_counter += 1
        return f"mock_access_{user_id}_{role}_{self.access_counter}"

    def create_refresh_token(self, user_id: int):
        self.refresh_counter += 1
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        return f"mock_refresh_{user_id}_{self.refresh_counter}", expires_at