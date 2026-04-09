from datetime import datetime

from pydantic import BaseModel


class RunRequest(BaseModel):
    language: str
    code: str
    stdin: str
    submitted_at: datetime


class RunResponse(BaseModel):
    stdout: str | None = None
    stderr: str | None = None
    compile_output: str | None = None
