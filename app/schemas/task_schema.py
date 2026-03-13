from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[datetime] = None


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    task_id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    created_at: datetime


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]


class TaskMessageResponse(BaseModel):
    message: str
