from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import session_generator
from app.database.models import TaskTest

class TaskTestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_task_id(self, task_id: int) -> list[TaskTest]:
        result = await self.db.execute(
            select(TaskTest).where(TaskTest.task_id == task_id)
        )
        return result.scalars().all()

    async def get_by_id(self, test_id: int) -> TaskTest | None:
        result = await self.db.execute(
            select(TaskTest).where(TaskTest.id == test_id)
        )
        return result.scalars().first()

    async def get_by_id_and_task(self, test_id: int, task_id: int) -> TaskTest | None:
        result = await self.db.execute(
            select(TaskTest).where(
                TaskTest.id == test_id,
                TaskTest.task_id == task_id,
            )
        )
        return result.scalars().first()

    async def add(self, test: TaskTest) -> None:
        self.db.add(test)

    async def add_all(self, tests: list[TaskTest]) -> None:
        self.db.add_all(tests)

    async def delete(self, test: TaskTest) -> None:
        await self.db.delete(test)

def get_task_test_repository(
    db: AsyncSession = Depends(session_generator),
) -> TaskTestRepository:
    return TaskTestRepository(db)
