from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task
from app.repositories.base import BaseRepository
from app.schemas.task import TaskCreate, TaskFilterParams


class TaskRepository(BaseRepository[Task]):
    def __init__(self):
        super().__init__(Task)

    async def get_by_id_and_user(
        self,
        db: AsyncSession,
        *,
        task_id: int,
        user_id: int,
    ) -> Optional[Task]:
        """Fetch a task only if it belongs to the given user."""
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_user_tasks_filtered(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        filter_params: TaskFilterParams,
    ) -> Tuple[List[Task], int]:
        """Fetch filtered, searched, sorted, and paginated tasks for a specific user."""
        base_query = select(Task).where(Task.user_id == user_id)

        # Filter by Status
        if filter_params.status is not None:
            base_query = base_query.where(Task.status == filter_params.status)

        # Filter by Priority
        if filter_params.priority is not None:
            base_query = base_query.where(Task.priority == filter_params.priority)

        # Keyword Search in Title or Description
        if filter_params.search:
            search_pattern = f"%{filter_params.search.strip()}%"
            base_query = base_query.where(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern),
                )
            )

        # Count total matching rows
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count_result = await db.execute(count_query)
        total_count = total_count_result.scalar_one()

        # Sorting
        sort_column = getattr(Task, filter_params.sort_by, Task.created_at)
        if filter_params.sort_order.lower() == "desc":
            sort_column = sort_column.desc().nulls_last()
        else:
            sort_column = sort_column.asc().nulls_first()

        paginated_query = (
            base_query.order_by(sort_column)
            .offset((filter_params.page - 1) * filter_params.page_size)
            .limit(filter_params.page_size)
        )

        result = await db.execute(paginated_query)
        tasks = list(result.scalars().all())

        return tasks, total_count

    async def create_user_task(
        self,
        db: AsyncSession,
        *,
        task_in: TaskCreate,
        user_id: int,
    ) -> Task:
        """Create a new task assigned to the specified user."""
        task_data = task_in.model_dump()
        task_data["user_id"] = user_id
        return await self.create(db, obj_in=task_data)


task_repo = TaskRepository()
