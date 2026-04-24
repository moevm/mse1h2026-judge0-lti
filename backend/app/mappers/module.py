from app.database.models import Module, ModuleTaskOrder, Task
from app.schemas.module import ModuleResponse, ModuleWithTaskIdResponse
from app.schemas.task import TaskResponse


class ModuleMapper:
    @staticmethod
    def to_module_with_task_ids(module: Module) -> ModuleWithTaskIdResponse:
        return ModuleWithTaskIdResponse(
            id=module.id,
            title=module.title,
            description=module.description,
            created_at=module.created_at,
            updated_at=module.updated_at,
            tasks=[link.task_id for link in module.task_links],
        )

    @staticmethod
    def to_module_with_tasks(module: Module) -> ModuleResponse:
        return ModuleResponse(
            id=module.id,
            title=module.title,
            description=module.description,
            created_at=module.created_at,
            updated_at=module.updated_at,
            tasks=[
                TaskResponse.model_validate(link.task)
                for link in module.task_links
            ],
        )

    @staticmethod
    def to_task_list(tasks: list[Task]) -> list[TaskResponse]:
        return [TaskResponse.model_validate(t) for t in tasks]