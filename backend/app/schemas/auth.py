from pydantic import BaseModel


class AuthRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    access_token: str

class TokenUser(BaseModel):
    user_id: int
    role: str
