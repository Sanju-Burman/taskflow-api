import math
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundException
from app.models.task import Task
from app.repositories.task_repo import task_repo
from app.schemas.base import PaginatedMeta, PaginatedResponse
from app.schemas.task import (
    TaskCreate,
    TaskFilterParams,
    TaskPartialUpdate,
    TaskRead,
    TaskUpdate,
)


class TaskService:
    async def create_task(
        self,
        db: AsyncSession,
        *,
        task_in: TaskCreate,
        user_id: int,
    ) -> Task:
        return await task_repo.create_user_task(db, task_in=task_in, user_id=user_id)

    async def get_task(
        self,
        db: AsyncSession,
        *,
        task_id: int,
        user_id: int,
    ) -> Task:
        task = await task_repo.get_by_id_and_user(db, task_id=task_id, user_id=user_id)
        if not task:
            raise NotFoundException("Task not found or access denied.")
        return task

    async def list_tasks(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        filter_params: TaskFilterParams,
    ) -> PaginatedResponse[TaskRead]:
        tasks, total_count = await task_repo.get_user_tasks_filtered(
            db,
            user_id=user_id,
            filter_params=filter_params,
        )

        total_pages = math.ceil(total_count / filter_params.page_size) if total_count > 0 else 1
        has_next = filter_params.page < total_pages
        has_prev = filter_params.page > 1

        pagination = PaginatedMeta(
            total=total_count,
            page=filter_params.page,
            page_size=filter_params.page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
        )

        return PaginatedResponse(
            success=True,
            data=[TaskRead.model_validate(t) for t in tasks],
            pagination=pagination,
        )

    async def update_task(
        self,
        db: AsyncSession,
        *,
        task_id: int,
        user_id: int,
        task_in: Union[TaskUpdate, TaskPartialUpdate],
    ) -> Task:
        task = await self.get_task(db, task_id=task_id, user_id=user_id)
        return await task_repo.update(db, db_obj=task, obj_in=task_in)

    async def delete_task(
        self,
        db: AsyncSession,
        *,
        task_id: int,
        user_id: int,
    ) -> Task:
        task = await self.get_task(db, task_id=task_id, user_id=user_id)
        await task_repo.remove(db, id=task.id)
        return task


task_service = TaskService()
