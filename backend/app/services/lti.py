from fastapi import Depends
from app.database.models import User, UserTypeEnum
from app.repositories.user import UserRepository, get_user_repository


def map_role(roles: str) -> UserTypeEnum:
    if "Instructor" in roles:
        return UserTypeEnum.admin
    if "Teacher" in roles:
        return UserTypeEnum.teacher
    return UserTypeEnum.student


class LtiService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def upsert_user(
        self, user_id: int, username: str, full_name: str, roles: str
    ) -> User:
        role = map_role(roles)

        user = self.repo.get_by_id(user_id)

        if not user:
            user = User(id=user_id, username=username, full_name=full_name, role=role)
            self.repo.add(user)
        else:
            user.username = username
            user.full_name = full_name
            user.role = role

        return user


def get_lti_service(repo: UserRepository = Depends(get_user_repository)) -> LtiService:
    return LtiService(repo)
