from typing import List

from app.database.models import Task

from app.schemas.task import TaskResponse, TaskTestResponse


class TaskMapper:

    @staticmethod
    def to_task_response(task: Task) -> TaskResponse:
        return TaskResponse.model_validate(task)

    @staticmethod
    def to_task_list_response(tasks: List[Task]) -> List[TaskResponse]:
        return [TaskResponse.model_validate(task) for task in tasks]

    @staticmethod
    def to_task_tests_list_response(task: Task) -> List[TaskTestResponse]:
        return [TaskTestResponse.model_validate(test) for test in task.tests]
