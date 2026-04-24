from typing import List

from pydantic import BaseModel, ConfigDict

class TaskTestCreate(BaseModel):
    title: str
    stdin: str = ""
    stdout: str
    model_config = ConfigDict(extra="forbid")

class TaskTestPatch(BaseModel):
    title: str | None = None
    stdin: str | None = None
    stdout: str | None = None
    model_config = ConfigDict(extra="forbid")

class TaskTestResponse(BaseModel):
    id: int
    title: str
    stdin: str
    stdout: str
    model_config = ConfigDict(from_attributes=True)

class TaskTestFileSchema(BaseModel):
    tests: List[TaskTestCreate]

    model_config = ConfigDict(extra="forbid")