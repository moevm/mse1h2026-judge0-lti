from typing import List

from app.database.models import Task

from app.schemas.task import TaskResponse


class TaskMapper:

    @staticmethod
    def to_task_response(task: Task) -> TaskResponse:
        return TaskResponse.model_validate(task)

    @staticmethod
    def to_task_list_response(tasks: List[Task]) -> List[TaskResponse]:
        return [TaskResponse.model_validate(task) for task in tasks]
