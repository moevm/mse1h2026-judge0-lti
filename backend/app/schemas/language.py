from pydantic import BaseModel, ConfigDict


class LanguageResponse(BaseModel):
    language: str

    model_config = ConfigDict(from_attributes=True)
