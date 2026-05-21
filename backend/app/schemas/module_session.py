from datetime import datetime

from pydantic import BaseModel, ConfigDict

class ModuleSessionBase(BaseModel):
    id: int
    user_id: int
    module_id: int
    started_at: datetime
    expires_at: datetime
    finished_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class ModuleSessionResponse(BaseModel):
    session: ModuleSessionBase | None
    server_time_now: datetime