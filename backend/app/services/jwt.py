import jwt
import os
from datetime import datetime, timedelta, timezone

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret")
ALGORITHM = "HS256"
EXPIRE_HOURS = 24


class JwtService:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.expire_hours = EXPIRE_HOURS

    def create_token(self, user_id: int) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=self.expire_hours)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> int:
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        return payload["user_id"]


def get_jwt_service() -> JwtService:
    return JwtService()
