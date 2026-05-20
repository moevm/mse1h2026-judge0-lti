from app.core.exceptions.base import BadRequestException


class LtiVerificationError(BadRequestException):
    default_detail = "Ошибка верификации LTI токена"