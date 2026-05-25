from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class CheckRequest(BaseModel):
    language: str
    code: str
    submitted_at: datetime


class SubmitResponse(BaseModel):
    tokens: list[str]
    task_id: int
    user_id: int
    solution_id: int
    language_id: int
    language: str


class ResultRequest(BaseModel):
    tokens: list[str]
    solution_id: int
    language_id: int
    language: str
    code: str


class CheckResponse(BaseModel):
    done: bool
    success: bool | None = None
    error: str | None = None
    comment: str | None = None
    passed: str | None = None
    attempts_used: int | None = None
    max_attempts: int | None = None


class AttemptsInfoResponse(BaseModel):
    attempts_used: int
    max_attempts: int | None
