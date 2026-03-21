from pydantic import BaseModel, ConfigDict


class LanguageResponse(BaseModel):
    id: int
    language: str

    model_config = ConfigDict(from_attributes=True)
