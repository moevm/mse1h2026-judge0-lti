from app.schemas.check import CheckResponse, AttemptsInfoResponse
from app.services.check import CheckResult, AttemptsInfo


class CheckMapper:
    @staticmethod
    def to_response(result: CheckResult) -> CheckResponse:
        return CheckResponse(
            done=True,
            success=result.success,
            error=result.error,
            comment=result.comment,
            passed=f"{result.passed}/{result.total} тестов пройдено",
            attempts_used=result.attempts_used,
            max_attempts=result.max_attempts,
        )

    @staticmethod
    def to_attempts_response(result: AttemptsInfo) -> AttemptsInfoResponse:
        return AttemptsInfoResponse(
            attempts_used=result.attempts_used,
            max_attempts=result.max_attempts,
        )
