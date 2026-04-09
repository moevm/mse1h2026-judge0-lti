from datetime import datetime

from pydantic import BaseModel


class RunRequest(BaseModel):
    language: str
    code: str
    stdin: str
    submitted_at: datetime


class RunResponse(BaseModel):
    stdout: str = None
    stderr: str = None
    compile_output: str = None
