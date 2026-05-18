from app.core.exceptions.base import ServerException


class JudgeException(ServerException):
    default_detail = "Ошибка связи с Judge0"
