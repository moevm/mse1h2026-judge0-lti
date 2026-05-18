from app.core.exceptions.base import NotFoundException, BadRequestException


class TaskNotFoundException(NotFoundException):
    default_detail = "Задача не найдена"


class TaskTestNotFoundException(NotFoundException):
    default_detail = "Тест не найден"


class InvalidLanguageException(BadRequestException):
    default_detail = "Указан недопустимый язык программирования"


class InvalidTaskTestsFileException(BadRequestException):
    default_detail = "Некорректный JSON файл"
