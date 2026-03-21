from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CheckRequest(BaseModel):
    language: str
    code: str
    submitted_at: datetime
    
class CheckResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    comment: str | None = None
    passed: str