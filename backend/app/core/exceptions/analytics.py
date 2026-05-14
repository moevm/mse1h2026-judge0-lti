from app.core.exceptions.base import AppException


class AttemptNotFoundException(AppException):
    status_code = 404
    default_detail = "Попытка не найдена"
