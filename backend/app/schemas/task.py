from fastapi import Query
from pydantic import BaseModel, ConfigDict, field_validator, Field
from datetime import datetime
from typing import Optional, List

from app.schemas.task_test import TaskTestResponse, TaskTestCreate

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    timeout: int
    languages: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    tests: List[TaskTestResponse]
    model_config = ConfigDict(from_attributes=True)

    @field_validator("languages", mode="before")
    @classmethod
    def extract_languages(cls, languages):
        return [l.language for l in languages]


class TaskPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    timeout: int | None = Field(None, ge=0)
    languages: List[str] | None = None
    tests: List[TaskTestCreate] | None = None

    model_config = ConfigDict(extra="forbid")


class TaskCreate(BaseModel):
    title: str
    description: str
    timeout: int = Field(ge=0)
    languages: List[str]
    tests: List[TaskTestCreate] | None = None
    model_config = ConfigDict(extra="forbid")


class TaskFilter(BaseModel):
    search: str | None = None
    timeout_from: int | None = None
    timeout_to: int | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    updated_from: datetime | None = None
    updated_to: datetime | None = None
    model_config = ConfigDict(extra="forbid")
