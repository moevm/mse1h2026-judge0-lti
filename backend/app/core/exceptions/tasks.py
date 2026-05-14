from app.core.exceptions.base import AppException


class TaskNotFoundException(AppException):
    status_code = 404
    detail = "Задача не найдена"


class TaskTestNotFoundException(AppException):
    status_code = 404
    detail = "Тест не найден"


class InvalidLanguageException(AppException):
    status_code = 400
    detail = "Указан недопустимый язык программирования"


class InvalidTaskTestsFileException(AppException):
    status_code = 400
    detail = "Некорректный JSON файл"
