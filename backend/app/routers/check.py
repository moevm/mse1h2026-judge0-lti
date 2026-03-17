import os 
import requests
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import session_generator
from app.database.models import Task, Language
from app.schemas.check import CheckRequest, CheckResponse

router = APIRouter(prefix="/check", tags=["check"])

JUDGE0_URL = os.getenv("JUDGE0_URL", "http://judge0_server:2358")
MOCK_JUDGE0 = os.getenv("MOCK_JUDGE0", "false") == "true" # зашлушка пока не сделают джадж

def submit_to_judge0(source_code: str, language_id: int, stdin: str, timeout: int):
    if MOCK_JUDGE0:
        # возвращаем такую же структуру как Judge0
        return {
            "stdout": "mocked",
            "stderr": None,
            "status": {"id": 3, "description": "Accepted"}
        }

    #   отправляем пост запрос к Judge0
    response = requests.post(f"{JUDGE0_URL}/submissions?wait=true", json={
        "source_code": source_code,   # код студента
        "language_id": language_id,   # числовой ID
        "stdin": stdin,               # входные данные теста из пайплайна задачи
        "cpu_time_limit": timeout     # лимит времени из задачи
    })

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Ошибка связи с Judge0")

    return response.json()


@router.post("/{task_id}", response_model=CheckResponse)
async def check_solution(task_id: int, body: CheckRequest, db: Session = Depends(session_generator)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    language = db.query(Language).filter(Language.language == body.language).first()
    language_names = [lang.language for lang in task.languages]
    # print(f"\nDEBUG language: {language}")
    # print(f"DEBUG language.language: {language.language if language else None}")
    # print(f"DEBUG language_names: {language_names}")
    if not language or language.language not in language_names:
        raise HTTPException(status_code=400, detail="Недопустимый язык программирования для этой задачи")
    
    tests = task.tests_pipeline
    total = len(tests)
    passed =0
    
    for test in tests:
        #достаём входные данные теста
        stdin = test["input"]["stdin"]
        #достаём ожидаемый результат
        expected = test["output"]["stdout"].strip()
        result = submit_to_judge0(body.code, language.id, stdin, task.timeout)
        
                # ошибка компиляции или runtime
                #статус 3 и 4 - это Accepted и Wrong Answer, остальные - это ошибки
        if result["status"]["id"] not in (3, 4):
            return CheckResponse(
                success=False,
                error=result.get("stderr") or result.get("compile_output") or "Ошибка выполнения",
                comment=f'Тест "{test["title"]}" — {result["status"]["description"]}',
                passed=f"{passed}/{total} тестов пройдено"
            )

        stdout = (result.get("stdout") or "").strip()
        if stdout == expected:
            passed += 1
        else:
            return CheckResponse(
                success=False,
                error=None,
                comment=f'Тест "{test["title"]}" не прошёл. Ожидалось: "{expected}", получено: "{stdout}"',
                passed=f"{passed}/{total} тестов пройдено"
            )

    # все тесты прошли
    return CheckResponse(
        success=True,
        error=None,
        comment="Все тесты пройдены",
        passed=f"{passed}/{total} тестов пройдено"
    )