import base64
import requests
from fastapi.params import Depends

from app.config import Settings, get_settings


class Judge0Exception(Exception):
    pass


class JudgeService:
    def __init__(self, settings: Settings):
        self.judge0_url = settings.judge0_url
        self.mock_judge0 = settings.mock_judge0 == "true"

    def submit(
        self, source_code: str, language_id: int, stdin: str, timeout: int
    ) -> dict:
        if self.mock_judge0:
            return {
                "stdout": "mocked",
                "stderr": None,
                "status": {"id": 3, "description": "Accepted"},
            }
        # кодируем код и stdin в base64
        encoded_code = base64.b64encode(source_code.encode("utf-8")).decode()
        encoded_stdin = base64.b64encode(stdin.encode("utf-8")).decode()
        response = requests.post(
            f"{self.judge0_url}/submissions?wait=true",
            json={
                "source_code": encoded_code,
                "language_id": language_id,
                "stdin": encoded_stdin,
                "cpu_time_limit": timeout,
                "base64_encoded": True,  # говорим Judge0 что всё в base64
            },
        )

        if response.status_code not in (200, 201):
            raise Judge0Exception

        result = response.json()
        # декодируем ответ из base64
        if result.get("stdout"):
            result["stdout"] = base64.b64decode(result["stdout"]).decode("utf-8")
        if result.get("stderr"):
            result["stderr"] = base64.b64decode(result["stderr"]).decode("utf-8")
        if result.get("compile_output"):
            result["compile_output"] = base64.b64decode(
                result["compile_output"]
            ).decode("utf-8")

        return result


def get_judge_service(settings: Settings = Depends(get_settings)) -> JudgeService:
    return JudgeService(settings)
