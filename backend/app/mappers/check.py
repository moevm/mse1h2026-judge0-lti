from app.schemas.check import CheckResponse
from app.services.check import CheckResult


class CheckMapper:
    @staticmethod
    def to_response(result: CheckResult) -> CheckResponse:
        return CheckResponse(
            success=result.success,
            error=result.error,
            comment=result.comment,
            passed=f"{result.passed}/{result.total} тестов пройдено",
        )
