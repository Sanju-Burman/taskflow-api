from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.task import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the task")
    description: Optional[str] = Field(None, max_length=5000, description="Detailed description")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority level")
    due_date: Optional[datetime] = Field(None, description="Due date in ISO 8601 format")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


class TaskPartialUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskRead(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskFilterParams(BaseModel):
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    sort_by: str = Field(default="created_at", pattern="^(created_at|due_date|priority|title)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
