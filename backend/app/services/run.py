from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.services.judge import JudgeService
from app.schemas.run import RunRequest
from app.database.models import Language
from app.database.database import session_generator
from app.services.judge import get_judge_service


class RunService:
    def __init__(self, db: Session, judge: JudgeService) -> None:
        self.db = db
        self.judge = judge

    def run_code(self, body: RunRequest):
        language = (
            self.db.query(Language).filter(Language.language == body.language).first()
        )
        return self.judge.submit(body.code, language.id, body.stdin, 5)


def get_run_service(
    db: Session = Depends(session_generator),
    judge: JudgeService = Depends(get_judge_service),
) -> RunService:
    return RunService(db, judge)
