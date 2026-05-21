from typing import List
from fastapi import Depends

from app.repositories.solution import SolutionRepository, get_solution_repository
from app.repositories.attempt import AttemptRepository, get_attempt_repository
from app.schemas.solution import SolutionFilter
from app.database.models import Solution, Attempt
from app.core.exceptions.tasks import TaskNotFoundException


class SolutionService:
    def __init__(self, repo: SolutionRepository, attempt_repo: AttemptRepository):
        self.repo = repo
        self.attempt_repo = attempt_repo

    def get_solutions_by_task(self, task_id: int, filters: SolutionFilter) -> List[Solution]:
        return self.repo.get_by_task_id_with_filters(task_id, filters)

    def get_solution_attempts(self, solution_id: int) -> List[Attempt]:
        solution = self.repo.get_by_id(solution_id)
        if not solution:
            raise TaskNotFoundException(f"Решение {solution_id} не найдено")
        return self.attempt_repo.get_by_solution_id(solution_id)


def get_solution_service(
    repo: SolutionRepository = Depends(get_solution_repository),
    attempt_repo: AttemptRepository = Depends(get_attempt_repository),
) -> SolutionService:
    return SolutionService(repo, attempt_repo)
