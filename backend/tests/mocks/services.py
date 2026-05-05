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

    def decode_access_token(self, token: str):
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "")

        if token.startswith("mock_access_"):
            parts = token.split("_")
            if len(parts) >= 4:
                return {"user_id": int(parts[2]), "role": parts[3], "type": "access"}

        if token == "expired_token":
            from jwt.exceptions import ExpiredSignatureError

            raise ExpiredSignatureError("Token expired")

        if token == "invalid_token":
            from jwt.exceptions import InvalidTokenError

            raise InvalidTokenError("Invalid token")

        return {"user_id": 1, "role": "student", "type": "access"}
