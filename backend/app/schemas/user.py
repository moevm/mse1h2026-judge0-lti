from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Literal
from app.database.models import UserTypeEnum


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    role: UserTypeEnum
    solved_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class UserFilter(BaseModel):
    search: Optional[str] = None
    include_deleted: bool = False


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserTypeEnum] = None
