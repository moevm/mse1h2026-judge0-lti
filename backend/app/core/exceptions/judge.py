from app.core.exceptions.base import AppException


class JudgeException(AppException):
    status_code = 500
    default_detail = "Ошибка связи с Judge0"
