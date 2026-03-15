from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.language import LanguageResponse

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    timeout: int
    languages: list[LanguageResponse]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True