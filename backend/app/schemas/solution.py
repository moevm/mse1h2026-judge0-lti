from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict


class SolutionFilter(BaseModel):
    is_solved: Optional[bool] = None
    score_min: Optional[int] = None
    score_max: Optional[int] = None
    updated_from: Optional[datetime] = None
    updated_to: Optional[datetime] = None
    sort_by: Optional[Literal["id", "score", "is_solved", "created_at", "updated_at"]] = "created_at"
    sort_order: Literal["asc", "desc"] = "desc"
    model_config = ConfigDict(extra="forbid")


class SolutionWithUserResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    username: str
    full_name: str
    is_solved: bool
    score: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
