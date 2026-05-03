from fastapi import APIRouter, Depends, HTTPException, Header
from app.services.users import UserService, get_user_service, UserNotFoundException
from app.schemas.user import UserResponse, UserFilter, UserUpdateRequest
from app.mappers.user import UserMapper
from app.services.jwt import JwtService, get_jwt_service
from app.core.dependencies import get_current_user_payload, get_current_admin
from app.schemas.auth import TokenUser
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
        user_id = jwt_service.decode_access_token(token)["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истёк")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Невалидный токен")

    try:
        user, solved_count = service.get_with_solved_count(user_id)
        return UserMapper.to_response(user, solved_count)
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Получить всех пользователей",
    description=(
        "Возвращает список всех пользователей с их ID, ФИО, ником, ролью и количеством решённых задач. "
        "Доступно только для администратора. "
        "Поддерживает фильтрацию:\n"
        "- **search** - поиск по части ФИО или никнейма (регистронезависимый)\n"
        "- **include_deleted** - показывать мягко удалённых пользователей (true/false)"
    )
)
def get_all_users(
    filters: UserFilter = Depends(),
    current_user: TokenUser = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    rows = service.get_all(filters)
    return [UserMapper.to_response(user, solved_count) for user, solved_count in rows]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Получить пользователя по ID",
    description=(
        "Возвращает ФИО, ник, роль, ID и количество решённых задач для указанного пользователя. "
        "Доступно только для администратора."
    )
)
def get_user(
    user_id: int,
    current_user: TokenUser = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    try:
        user, solved_count = service.get_with_solved_count(user_id)
        return UserMapper.to_response(user, solved_count)
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Изменить профиль пользователя",
    description=(
        "Обновляет данные пользователя. Админ может изменять ФИО и роль. "
        "Тело запроса может содержать одно или оба поля:\n"
        "- **full_name** - новое ФИО (string)\n"
        "- **role** - новая роль (admin/student/teacher)"
    )
)
def update_user(
    user_id: int,
    body: UserUpdateRequest,
    current_user: TokenUser = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    try:
        user = service.update(user_id, body)
        solved_count = service.repo.get_solved_count(user_id)
        return UserMapper.to_response(user, solved_count)
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Удалить пользователя (мягкое удаление)",
    description=(
        "Мягко удаляет пользователя - устанавливает timestamp в поле deleted_at. "
        "Пользователь не удаляется из БД, но скрывается из списков. "
    )
)
def delete_user(
    user_id: int,
    current_user: TokenUser = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    try:
        service.delete(user_id)
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
