from fastapi.params import Depends
import jwt
from datetime import datetime, timedelta, timezone
from app.config import Settings, get_settings

ALGORITHM = "HS256"
EXPIRE_HOURS = 24


class JwtService:
    def __init__(self, settings: Settings) -> None:
        self.secret_key = settings.jwt_secret_key
        self.algorithm = ALGORITHM
        self.expire_hours = EXPIRE_HOURS
        self.access_expire_minutes = settings.access_token_expire_minutes
        self.refresh_expire_days = settings.refresh_token_expire_days

    def create_access_token(self, user_id: int, role: str) -> str:
        payload = {
            "user_id": user_id,
            "role": role,
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=self.access_expire_minutes),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: int) -> tuple[str, datetime]:
        expire_at = datetime.now(timezone.utc) + timedelta(
            days=self.refresh_expire_days
        )
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "exp": expire_at,
        }
        token = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
        )

        return token, expire_at

    def decode_token(self, token: str) -> int:
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        return payload["user_id"]


def get_jwt_service(settings: Settings = Depends(get_settings)) -> JwtService:
    return JwtService(settings)
