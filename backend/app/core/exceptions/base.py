class AppException(Exception):
    status_code: int = 400
    default_detail: str = "Application error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail
        super().__init__(self.detail)
