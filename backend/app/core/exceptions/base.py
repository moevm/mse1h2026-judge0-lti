class AppException(Exception):
    status_code: int = 400
    default_detail: str = "Application error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class NotFoundException(AppException):
    status_code = 404


class BadRequestException(AppException):
    status_code = 400


class ServerException(AppException):
    status_code = 500

class ForbiddenException(AppException):
    status_code = 403