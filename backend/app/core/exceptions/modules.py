from app.core.exceptions.base import NotFoundException, BadRequestException


class ModuleNotFoundException(NotFoundException):
    default_detail = "Модуль не найден"


class TaskNotExistsException(NotFoundException):
    default_detail = "Одна или несколько задач не существуют"


class DuplicateTaskInRequestException(BadRequestException):
    default_detail = "В запросе есть дублирующиеся задачи"


class TaskAlreadyInModuleException(BadRequestException):
    default_detail = "В модуле уже присутствует данная задача"


class ModuleTasksMismatchException(BadRequestException):
    default_detail = "Переданный набор задач не соответствует модулю"
