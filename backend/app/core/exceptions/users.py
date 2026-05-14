from app.core.exceptions.base import AppException


class UserNotFoundException(AppException):
    status_code = 404
    default_detail = "Пользователь не найден"
