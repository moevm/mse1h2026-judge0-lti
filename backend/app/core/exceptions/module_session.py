from app.core.exceptions.base import ForbiddenException


class ModuleAttemptsExceededException(ForbiddenException):
    default_detail = "Максимальное количество попыток исчерпано"


class ModuleSessionNotActiveException(ForbiddenException):
    default_detail = "Сессия модуля не активна"