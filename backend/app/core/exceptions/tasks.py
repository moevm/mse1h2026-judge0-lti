from app.core.exceptions.base import AppException


class TaskNotFoundException(AppException):
    status_code = 404
    default_detail = "Задача не найдена"


class TaskTestNotFoundException(AppException):
    status_code = 404
    default_detail = "Тест не найден"


class InvalidLanguageException(AppException):
    status_code = 400
    default_detail = "Указан недопустимый язык программирования"


class InvalidTaskTestsFileException(AppException):
    status_code = 400
    default_detail = "Некорректный JSON файл"
