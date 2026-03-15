from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    timeout: int
    languages: list[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True