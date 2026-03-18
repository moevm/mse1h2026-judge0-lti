from pydantic import BaseModel


class LanguageResponse(BaseModel):
    language: str

    class Config:
        from_attributes = True
