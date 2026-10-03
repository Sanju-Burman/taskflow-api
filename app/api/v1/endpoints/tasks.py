from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import CurrentUserDep, SessionDep
from app.models.task import TaskPriority, TaskStatus
from app.schemas.base import BaseResponse, DataResponse, PaginatedResponse
from app.schemas.task import (
    TaskCreate,
    TaskFilterParams,
    TaskPartialUpdate,
    TaskRead,
    TaskUpdate,
)
from app.services.task_service import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get(
    "",
    response_model=PaginatedResponse[TaskRead],
    summary="List all tasks for current user with filtering, search & pagination",
)
async def list_tasks(
    db: SessionDep,
    current_user: CurrentUserDep,
    status: Annotated[TaskStatus | None, Query(description="Filter by task status")] = None,
    priority: Annotated[TaskPriority | None, Query(description="Filter by task priority")] = None,
    search: Annotated[str | None, Query(description="Search in task title and description")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
    sort_by: Annotated[
        str,
        Query(
            pattern="^(created_at|due_date|priority|title)$",
            description="Sort column: created_at, due_date, priority, title",
        ),
    ] = "created_at",
    sort_order: Annotated[
        str,
        Query(
            pattern="^(asc|desc)$",
            description="Sort direction: asc or desc",
        ),
    ] = "desc",
) -> PaginatedResponse[TaskRead]:
    """Retrieve a paginated list of tasks belonging exclusively to the authenticated user."""
    filter_params = TaskFilterParams(
        status=status,
        priority=priority,
        search=search,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return await task_service.list_tasks(
        db,
        user_id=current_user.id,
        filter_params=filter_params,
    )


@router.post(
    "",
    response_model=DataResponse[TaskRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
async def create_task(
    db: SessionDep,
    current_user: CurrentUserDep,
    task_in: TaskCreate,
) -> DataResponse[TaskRead]:
    """Create a new task assigned to the authenticated user."""
    task = await task_service.create_task(
        db,
        task_in=task_in,
        user_id=current_user.id,
    )
    return DataResponse(
        success=True,
        message="Task created successfully.",
        data=TaskRead.model_validate(task),
    )


@router.get(
    "/{task_id}",
    response_model=DataResponse[TaskRead],
    summary="Retrieve task details by ID",
)
async def get_task(
    db: SessionDep,
    current_user: CurrentUserDep,
    task_id: int,
) -> DataResponse[TaskRead]:
    """Get details of a specific task by its ID if owned by the authenticated user."""
    task = await task_service.get_task(
        db,
        task_id=task_id,
        user_id=current_user.id,
    )
    return DataResponse(
        success=True,
        data=TaskRead.model_validate(task),
    )


@router.put(
    "/{task_id}",
    response_model=DataResponse[TaskRead],
    summary="Full update of a task",
)
async def update_task(
    db: SessionDep,
    current_user: CurrentUserDep,
    task_id: int,
    task_in: TaskUpdate,
) -> DataResponse[TaskRead]:
    """Replace all editable fields of an existing task."""
    task = await task_service.update_task(
        db,
        task_id=task_id,
        user_id=current_user.id,
        task_in=task_in,
    )
    return DataResponse(
        success=True,
        message="Task updated successfully.",
        data=TaskRead.model_validate(task),
    )


@router.patch(
    "/{task_id}",
    response_model=DataResponse[TaskRead],
    summary="Partial update of a task",
)
async def partial_update_task(
    db: SessionDep,
    current_user: CurrentUserDep,
    task_id: int,
    task_in: TaskPartialUpdate,
) -> DataResponse[TaskRead]:
    """Partially update specific fields of a task (e.g. status or priority)."""
    task = await task_service.update_task(
        db,
        task_id=task_id,
        user_id=current_user.id,
        task_in=task_in,
    )
    return DataResponse(
        success=True,
        message="Task updated successfully.",
        data=TaskRead.model_validate(task),
    )


@router.delete(
    "/{task_id}",
    response_model=BaseResponse,
    summary="Delete a task",
)
async def delete_task(
    db: SessionDep,
    current_user: CurrentUserDep,
    task_id: int,
) -> BaseResponse:
    """Delete a task owned by the authenticated user."""
    await task_service.delete_task(
        db,
        task_id=task_id,
        user_id=current_user.id,
    )
    return BaseResponse(
        success=True,
        message=f"Task with ID {task_id} deleted successfully.",
    )
