from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_get_db
from app.core.dependency import get_current_user
from app.services.task_service import TaskService
from app.schemas.task_schema import *
import logging
from app.core.config import CustomAPIException


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Tasks"])

task_service = TaskService()

@router.post("/create_task", response_model=TaskMessageResponse)
async def create_task_api(task_data: TaskCreateRequest, user_data: dict = Depends(get_current_user), db: AsyncSession = Depends(async_get_db)):
    try:
        return await task_service.create_task(db, user_data["user_id"], task_data)
    except CustomAPIException as e:
        logger.error(f"CustomError:", exc_info=e)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        logger.exception(f"Unexpected error:", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/get_tasks", response_model=TaskListResponse)
async def get_tasks_api(user_data: dict = Depends(get_current_user), db: AsyncSession = Depends(async_get_db)):
    try:
        return await task_service.get_tasks(db, user_data["user_id"])
    except CustomAPIException as e:
        logger.error(f"CustomError:", exc_info=e)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        logger.exception(f"Unexpected error:", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))



@router.put("/update_task/{task_id}", response_model=TaskMessageResponse)
async def update_task_api(task_id: str, task_data: TaskUpdateRequest, user_data: dict = Depends(get_current_user), db: AsyncSession = Depends(async_get_db)):
    try:
        return await task_service.update_task(db, user_data["user_id"], task_id, task_data)
    except CustomAPIException as e:
        logger.error(f"CustomError:", exc_info=e)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        logger.exception(f"Unexpected error:", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_task/{task_id}", response_model=TaskMessageResponse)
async def delete_task_api(task_id: str, user_data: dict = Depends(get_current_user), db: AsyncSession = Depends(async_get_db)):
    try:
        return await task_service.delete_task(db, user_data["user_id"], task_id)
    except CustomAPIException as e:
        logger.error(f"CustomError:", exc_info=e)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        logger.exception(f"Unexpected error:", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))