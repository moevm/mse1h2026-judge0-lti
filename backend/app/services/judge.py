import asyncio
import base64
import time

import httpx
from fastapi import Request
from fastapi.params import Depends
from app.core.config import Settings, get_settings
from app.core.exceptions.judge import JudgeException


class JudgeService:
    def __init__(self, settings: Settings, client: httpx.AsyncClient):
        self.judge0_url = settings.judge0_url
        self.client = client
        self.mock_judge0 = settings.mock_judge0 == "true"

    def _encode(self, text: str) -> str:
        return base64.b64encode(text.encode("utf-8")).decode()

    def _decode(self, text: str | None) -> str | None:
        if not text:
            return None
        return base64.b64decode(text).decode("utf-8")

    def _decode_result(self, result: dict) -> dict:
        result["stdout"] = self._decode(result.get("stdout"))
        result["stderr"] = self._decode(result.get("stderr"))
        result["compile_output"] = self._decode(result.get("compile_output"))
        return result

    async def submit(
        self, source_code: str, language_id: int, stdin: str, timeout: int
    ) -> dict:
        if self.mock_judge0:
            return {
                "stdout": "mocked",
                "stderr": None,
                "compile_output": None,
                "status": {"id": 3, "description": "Accepted"},
            }

        tokens = await self.submit_batch(
            source_code=source_code,
            language_id=language_id,
            tests=[{"stdin": stdin}],
            timeout=timeout,
        )
        results = await self.poll_batch(tokens)
        return results[0]

    async def submit_batch(
        self,
        source_code: str,
        language_id: int,
        tests: list[dict],
        timeout: int,
    ) -> list[str]:
        if self.mock_judge0:
            return [f"mock-token-{i}" for i in range(len(tests))]

        submissions = [
            {
                "source_code": self._encode(source_code),
                "language_id": language_id,
                "stdin": self._encode(test["stdin"] or ""),
                "cpu_time_limit": timeout,
                "base64_encoded": True,
            }
            for test in tests
        ]

        response = await self.client.post(
            f"{self.judge0_url}/submissions/batch?base64_encoded=true",
            json={"submissions": submissions},
        )

        if response.status_code not in (200, 201):
            raise JudgeException()

        return [item["token"] for item in response.json()]

    async def fetch_batch(self, tokens: list[str]) -> list[dict]:
        """Один запрос к judge0 без ожидания."""
        if self.mock_judge0:
            return [
                {
                    "stdout": "mocked",
                    "stderr": None,
                    "compile_output": None,
                    "status": {"id": 3, "description": "Accepted"},
                }
                for _ in tokens
            ]

        response = await self.client.get(
            f"{self.judge0_url}/submissions/batch",
            params={"tokens": ",".join(tokens), "base64_encoded": "true"},
            timeout=10.0,
        )

        if response.status_code != 200:
            raise JudgeException()

        return [self._decode_result(r) for r in response.json()["submissions"]]

    async def poll_batch(
        self, tokens: list[str], interval: float = 0.5, timeout: float = 60.0
    ) -> list[dict]:
        deadline = time.monotonic() + timeout

        while True:
            if time.monotonic() > deadline:
                raise JudgeException()

            response = await self.client.get(
                f"{self.judge0_url}/submissions/batch",
                params={"tokens": ",".join(tokens), "base64_encoded": "true"},
            )

            if response.status_code != 200:
                raise JudgeException()

            results = [self._decode_result(r) for r in response.json()["submissions"]]

            if all(r["status"]["id"] > 2 for r in results):
                return results

            await asyncio.sleep(interval)


def get_judge_service(request: Request, settings: Settings = Depends(get_settings)):
    return JudgeService(settings, request.app.state.http_client)
