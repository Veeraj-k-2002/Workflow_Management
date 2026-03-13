from fastapi import APIRouter, Depends, HTTPException
from app.schemas.auth_schema import *
from app.schemas.auth_schema import UserBaseResponse
from app.services.auth_service import AuthService
from app.db.session import async_get_db
from app.core.dependency import JWTBearer, get_current_user
from app.core.config import CustomAPIException
from sqlalchemy.ext.asyncio import AsyncSession
import logging


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/authentication", tags=["authentication"])

auth_service = AuthService()


@router.post("/signup_user", response_model=SignupResponse)
async def signup_user_api(signup_data: SignupRequest, db: AsyncSession = Depends(async_get_db)):
    try:
        return await auth_service.signup_user(signup_data, db)
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        await db.rollback()
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login_api(login_data: LoginRequest, db: AsyncSession = Depends(async_get_db)):
    try:
        return await auth_service.login_user(login_data, db)
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout", response_model=CommonMessageResponse)
async def logout_api(db: AsyncSession = Depends(async_get_db), user_data : dict = Depends(get_current_user)):
    try:
        result = await auth_service.logout_user(db, user_data["user_id"])
        return result
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/get_profile_details",response_model= UserBaseResponse)
async def get_profile_details_api(user_data : dict = Depends(get_current_user), db: AsyncSession = Depends(async_get_db)):
    try:
        return await auth_service.get_user(db, user_data["user_id"])
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.delete("/delete_user/{user_id}", response_model=CommonMessageResponse)
async def delete_user_api(user_id: str, db: AsyncSession = Depends(async_get_db)):
    try:
        return await auth_service.delete_user(db, user_id)
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        await db.rollback()
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))
