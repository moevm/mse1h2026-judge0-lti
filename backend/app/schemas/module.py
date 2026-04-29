from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.task import TaskResponse


class ModuleBase(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ModuleCreate(BaseModel):
    title: str
    description: str

class ModulePatch(BaseModel):
    title: str | None = None
    description: str | None = None


class ModuleWithTaskIdResponse(ModuleBase):
    tasks: List[int]


class ModuleResponse(ModuleBase):
    tasks: List[TaskResponse]
