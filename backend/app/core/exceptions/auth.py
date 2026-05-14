from app.core.exceptions.base import AppException


class UnauthorizedException(AppException):
    status_code = 401
    default_detail = "Не авторизован"


class InvalidCredentialsException(UnauthorizedException):
    default_detail = "Неверный логин или пароль"


class InvalidRefreshTokenException(UnauthorizedException):
    default_detail = "Недействительный или просроченный refresh токен"


class RefreshTokenMissingException(UnauthorizedException):
    default_detail = "Отсутствует refresh токен"


class InvalidAccessTokenException(UnauthorizedException):
    default_detail = "Недействительный или просроченный access токен"


class InvalidTokenTypeException(UnauthorizedException):
    default_detail = "Неверный тип токена"
