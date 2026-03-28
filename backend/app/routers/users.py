from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database.database import session_generator
from app.database.models import User
from app.schemas.user import UserResponse
from app.services.jwt import decode_token
import jwt

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse, summary="Получаем текущего пользователя")
def get_me(
    authorization: str = Header(...),
    db: Session=Depends(session_generator)
):
    try:
        token = authorization.replace("Bearer", "")
        user_id = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истёк")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Невалидный токен")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
