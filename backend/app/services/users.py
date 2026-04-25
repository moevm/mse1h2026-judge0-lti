from fastapi import Depends
from app.database.models import User
from app.repositories.user import UserRepository, get_user_repository


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


def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repo)
