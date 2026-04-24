from app.database.models import Task

from app.schemas.task import TaskResponse


class TaskMapper:

    @staticmethod
    def to_task_response(task: Task) -> TaskResponse:
        return TaskResponse.model_validate(task)
