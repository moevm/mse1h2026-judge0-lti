from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.database.models import UserTypeEnum

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    role: UserTypeEnum
    created_at: datetime
    updated_at: Optional[datetime] = None
