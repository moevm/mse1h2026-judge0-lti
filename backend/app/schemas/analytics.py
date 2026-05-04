from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Literal


class UserModuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    task_count: int
    created_at: datetime


class UserTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    attempt_count: int
    is_solved: bool
    last_attempt_at: Optional[datetime] = None
    test_count: int


class AttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    message: Optional[str] = None
    status: Optional[str] = None
    exit_code: Optional[int] = None
    language: Optional[str] = None
    memory_kb: Optional[int] = None
    time_ms: Optional[int] = None
    is_solved: bool = False
    created_at: datetime
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    compile_output: Optional[str] = None


class UserModulesFilter(BaseModel):
    search: Optional[str] = Field(None)
    sort_by: Literal["name", "tasks_count", "created_at"] = "created_at"
    sort_order: Literal["asc", "desc"] = "asc"
    model_config = ConfigDict(extra="forbid")


class UserTasksFilter(BaseModel):
    search: Optional[str] = None
    attempt_count_min: Optional[int] = Field(None, ge=0)
    status: Optional[Literal["passed", "failed"]] = None
    last_attempt_from: Optional[datetime] = None
    last_attempt_to: Optional[datetime] = None
    test_count_min: Optional[int] = Field(None, ge=0)
    sort_by: Literal["title", "attempt_count", "last_attempt_at", "test_count"] = "title"
    sort_order: Literal["asc", "desc"] = "asc"
    model_config = ConfigDict(extra="forbid")


class AttemptsFilter(BaseModel):
    status: Optional[Literal["passed", "failed"]] = None
    language: Optional[str] = None
    memory_min: Optional[int] = Field(None, ge=0)
    memory_max: Optional[int] = Field(None, ge=0)
    time_min: Optional[int] = Field(None, ge=0)
    time_max: Optional[int] = Field(None, ge=0)
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    model_config = ConfigDict(extra="forbid")
