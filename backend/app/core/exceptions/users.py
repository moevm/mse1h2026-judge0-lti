from app.core.exceptions.base import NotFoundException


class UserNotFoundException(NotFoundException):
    default_detail = "Пользователь не найден"
