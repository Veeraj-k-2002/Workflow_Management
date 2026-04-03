from sqlalchemy.future import select
from sqlalchemy import delete
from app.schemas.task_schema import *
from datetime import datetime
from app.models.models import *
from app.core.config import CustomAPIException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

class TaskService:
    """
    Service class to handle CRUD operations for Tasks.

    Methods:
        create_task: Create a new task for a specific user.
        get_tasks: Fetch all tasks for a specific user.
        update_task: Update a task's details (status, priority, title, etc.).
        delete_task: Delete a task belonging to a user.
    """

    async def create_task(self, db: AsyncSession, user_id: str, task_data: TaskCreateRequest):
        """
        Create a new task for a given user.
        """
        existing_user = await db.get(User, user_id)
        if not existing_user:
            raise CustomAPIException(status_code=404, detail="Owner user not found")

        task = Task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            due_date=task_data.due_date,
            owner_id=user_id
        )

        db.add(task)
        await db.commit()

        return TaskMessageResponse(message="Task created successfully")


    async def get_tasks(self, db: AsyncSession, user_id: str):
        """
        Retrieve all tasks for a given user.
        """
        user = (
                    await db.execute(
                        select(User)
                        .options(joinedload(User.r_credentials))
                        .filter(User.id == user_id)
                    )
                ).scalar_one_or_none()

        if not user:
            raise CustomAPIException(404, "User not found")
        
        result = await db.execute(
            select(Task).where(Task.owner_id == user_id)
        )

        tasks = result.scalars().all()

        response = [
            TaskResponse(
                task_id=str(task.id),
                title=task.title,
                description=task.description,
                status=task.status,
                priority=task.priority,
                due_date=task.due_date,
                created_at=task.created_at
            )
            for task in tasks
        ]

        return TaskListResponse(tasks=response)


    async def update_task(self, db: AsyncSession, user_id: str, task_id: str, task_data: TaskUpdateRequest):
        """
        Update details of an existing task.
        """
        task = (
            await db.execute(
                select(Task).where(
                    Task.id == task_id,
                    Task.owner_id == user_id
                )
            )
        ).scalar_one_or_none()

        if not task:
            raise CustomAPIException(status_code=404, detail="Task not found")
        
        # valid_status = ["pending", "completed", "cancelled"]
        # valid_priority = ["low", "medium", "high"]

        # if task_data.status and task_data.status not in valid_status:
        #     raise CustomAPIException(400, "Invalid status")

        # if task_data.priority and task_data.priority not in valid_priority:
        #     raise CustomAPIException(400, "Invalid priority")


        for field, value in task_data.dict(exclude_unset=True).items():
            setattr(task, field, value)

        task.updated_at = datetime.utcnow()
        await db.commit()

        return TaskMessageResponse(message="Task updated successfully")


    async def delete_task(self, db: AsyncSession, user_id: str, task_id: str):
        """
        Delete a task belonging to a specific user.
        """
        result = await db.execute(
            delete(Task).where(
                Task.id == task_id,
                Task.owner_id == user_id
            )
        )

        if result.rowcount == 0:
            raise CustomAPIException(status_code=404, detail="Task not found")

        await db.commit()
        return TaskMessageResponse(message="Task deleted successfully")
