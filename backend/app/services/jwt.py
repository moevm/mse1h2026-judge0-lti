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

    def create_token(self, user_id: int) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=self.expire_hours),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> int:
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        return payload["user_id"]


def get_jwt_service(settings: Settings = Depends(get_settings)) -> JwtService:
    return JwtService(settings)
