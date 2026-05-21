from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AttemptResponse(BaseModel):
    id: int
    solution_id: int
    source_code: Optional[str] = None
    language: Optional[str] = None
    status: Optional[str] = None
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    compile_output: Optional[str] = None
    memory_kb: Optional[int] = None
    time_ms: Optional[int] = None
    is_solved: bool
    message: Optional[str] = None
    score: Optional[int] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
