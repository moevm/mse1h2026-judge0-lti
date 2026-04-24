from pydantic import BaseModel, ConfigDict, field_validator, Field
from datetime import datetime
from typing import Optional, List


class TaskTestCreate(BaseModel):
    title: str
    stdin: str = ""
    stdout: str
    model_config = ConfigDict(extra="forbid")

class TaskTestResponse(BaseModel):
    id: int
    title: str
    stdin: str
    stdout: str
    model_config = ConfigDict(from_attributes=True)

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    timeout: int
    languages: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    tests: list[TaskTestResponse]
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

    model_config = ConfigDict(extra="forbid")


class TaskCreate(BaseModel):
    title: str
    description: str
    timeout: int = Field(ge=0)
    languages: List[str]
    model_config = ConfigDict(extra="forbid")
