from .base import AppException


class UnauthorizedException(AppException):
    status_code = 401
    detail = "Не авторизован"


class InvalidCredentialsException(UnauthorizedException):
    detail = "Неверный логин или пароль"


class InvalidRefreshTokenException(UnauthorizedException):
    detail = "Недействительный или просроченный refresh токен"


class RefreshTokenMissingException(UnauthorizedException):
    detail = "Отсутствует refresh токен"
