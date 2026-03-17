from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    timeout: int
    languages: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator("languages", mode="before")
    @classmethod
    def extract_languages(cls, languages):
        return [l.language for l in languages]
