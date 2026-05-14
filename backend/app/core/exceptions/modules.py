from app.core.exceptions.base import AppException


class ModuleNotFoundException(AppException):
    status_code = 404
    default_detail = "Модуль не найден"


class TaskNotExistsException(AppException):
    status_code = 404
    default_detail = "Одна или несколько задач не существуют"


class DuplicateTaskInRequestException(AppException):
    status_code = 400
    default_detail = "В запросе есть дублирующиеся задачи"


class TaskAlreadyInModuleException(AppException):
    status_code = 400
    default_detail = "В модуле уже присутствует данная задача"


class ModuleTasksMismatchException(AppException):
    status_code = 400
    default_detail = "Переданный набор задач не соответствует модулю"
