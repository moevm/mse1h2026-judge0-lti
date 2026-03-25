from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.models import User, UserTypeEnum
from app.database.database import session_generator

def map_role(roles: str) -> UserTypeEnum:
    if "Instructor" in roles:
        return UserTypeEnum.admin
    if "Teacher" in roles:
        return UserTypeEnum.teacher
    return UserTypeEnum.student

class LtiServer:
    def __init__(self, db: Session):
        self.db = db

    def upsert_user(
        self,
        user_id: int,
        username: str,
        full_name: str,
        roles: str
    ) ->User:
        role = map_role(roles)
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            user = User(
                id=user_id,
                username=username,
                full_name=full_name,
                role=role
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        else:
            changed = False
            if user.role != role:
                user.role = role
                changed = True
            if user.full_name != full_name:
                user.full_name = full_name
                changed = True
            if user.username != username:
                user.username = username
                changed = True

            if changed:
                self.db.commit()
                self.db.refresh(user)
        return user

def get_lti_service(db: Session= Depends(session_generator)) -> LtiServer:
    return LtiServer(db)
