from fastapi import APIRouter, Depends

from app.database.models import UserTypeEnum
from app.services.users import UserService, get_user_service
from app.schemas.user import UserResponse, UserFilter, UserUpdateRequest
from app.mappers.user import UserMapper
from app.core.dependencies import get_current_user_payload, get_current_admin, require_roles
from app.schemas.auth import TokenUser

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: TokenUser = Depends(get_current_user_payload),
    service: UserService = Depends(get_user_service),
):
    user, solved_count = await service.get_with_solved_count(current_user.user_id)
    return UserMapper.to_response(user, solved_count)


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
    ),
)
async def get_all_users(
    filters: UserFilter = Depends(),
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: UserService = Depends(get_user_service),
):
    rows = await service.get_all(filters)
    return [UserMapper.to_response(user, solved_count) for user, solved_count in rows]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Получить пользователя по ID",
    description=(
        "Возвращает ФИО, ник, роль, ID и количество решённых задач для указанного пользователя. "
        "Доступно только для администратора."
    ),
)
async def get_user(
    user_id: int,
    user: TokenUser = Depends(require_roles(UserTypeEnum.admin, UserTypeEnum.teacher)),
    service: UserService = Depends(get_user_service),
):
    user, solved_count = await service.get_with_solved_count(user_id)
    return UserMapper.to_response(user, solved_count)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Изменить профиль пользователя",
    description=(
        "Обновляет данные пользователя. Админ может изменять ФИО и роль. "
        "Тело запроса может содержать одно или оба поля:\n"
        "- **full_name** - новое ФИО (string)\n"
        "- **role** - новая роль (admin/student/teacher)"
    ),
)
async def update_user(
    user_id: int,
    body: UserUpdateRequest,
    current_user: TokenUser = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    user = await service.update(user_id, body)
    solved_count = await service.repo.get_solved_count(user_id)
    return UserMapper.to_response(user, solved_count)


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Удалить пользователя (мягкое удаление)",
    description=(
        "Мягко удаляет пользователя - устанавливает timestamp в поле deleted_at. "
        "Пользователь не удаляется из БД, но скрывается из списков. "
    ),
)
async def delete_user(
    user_id: int,
    current_user: TokenUser = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    await service.delete(user_id)