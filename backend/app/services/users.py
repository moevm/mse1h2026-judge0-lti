from datetime import datetime, timezone
from fastapi import Depends
from app.database.models import User
from app.repositories.user import UserRepository, get_user_repository
from app.schemas.user import UserFilter, UserUpdateRequest


class UserNotFoundException(Exception):
    pass


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_by_id(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException
        return user

    def get_all(self, filters: UserFilter) -> list[tuple[User, int]]:
        users = self.repo.get_all(filters)
        return [(user, self.repo.get_solved_count(user.id)) for user in users]

    def get_with_solved_count(self, user_id: int) -> tuple[User, int]:
        user = self.get_by_id(user_id)
        return user, self.repo.get_solved_count(user_id)

    def update(self, user_id: int, body: UserUpdateRequest) -> User:
        user = self.get_by_id(user_id)
        if body.full_name is not None:
            user.full_name = body.full_name
        if body.role is not None:
            user.role = body.role
        return user

    def delete(self, user_id: int):
        user = self.get_by_id(user_id)
        user.deleted_at = datetime.now(timezone.utc)


def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repo)
