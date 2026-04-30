from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

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

class ModuleAddTasks(BaseModel):
    task_ids: List[int]

class TaskIdOrder(BaseModel):
    task_id: int
    order: int

class ModuleTasksReorder(BaseModel):
    tasks: List[TaskIdOrder]

    @model_validator(mode="after")
    def validate(self):
        orders = [t.order for t in self.tasks]
        if len(orders) != len(set(orders)):
            raise ValueError("duplicate order")
        if sorted(orders) != list(range(1, len(orders) + 1)):
            raise ValueError("orders must be sequential")
        return self
    def to_mapping(self) -> dict[int, int]:
        return {t.task_id: t.order for t in self.tasks}

class ModuleFilter(BaseModel):
    search: str | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    updated_from: datetime | None = None
    updated_to: datetime | None = None
    sort_by: Optional[Literal["created_at", "updated_at", "title"]] = (
        "created_at"
    )
    sort_order: Literal["asc", "desc"] = "desc"
    model_config = ConfigDict(extra="forbid")
