from app.database.models import User
from app.schemas.user import UserResponse


class UserMapper:
    @staticmethod
    def to_response(user: User) -> UserResponse:
        return UserResponse.model_validate(user)