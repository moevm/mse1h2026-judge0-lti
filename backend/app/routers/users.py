from fastapi import APIRouter, Depends, HTTPException, Header
from app.services.users import UserService, get_user_service, UserNotFoundException
from app.schemas.user import UserResponse
from app.services.jwt import JwtService, get_jwt_service
import jwt

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(
    authorization: str = Header(...),
    service: UserService = Depends(get_user_service),
    jwt_service: JwtService = Depends(get_jwt_service)
):
    try:
        token = authorization.replace("Bearer ", "")
        user_id = jwt_service.decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истёк")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Невалидный токен")

    try:
        return service.get_by_id(user_id)
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
