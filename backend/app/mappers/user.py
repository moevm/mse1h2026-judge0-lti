from app.database.models import User
from app.schemas.user import UserResponse


class UserMapper:
    @staticmethod
    def to_response(user: User, solved_count: int = 0) -> UserResponse:
        return UserResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            solved_count=solved_count,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
        )
