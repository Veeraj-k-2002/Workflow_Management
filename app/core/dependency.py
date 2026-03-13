from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from app.core.config import settings
from app.db.session import async_get_db
from app.models.models import User
from fastapi.security import HTTPBearer
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Tuple


class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        credentials = await super().__call__(request)

        if credentials is None:
            raise HTTPException(status_code=401, detail="Missing authorization credentials")

        token = credentials.credentials

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")


        return payload



# async def get_current_user(payload=Depends(JWTBearer())):
#     return {
#         "user_id": payload.get("user_id"),
#         "username": payload.get("username")
#     }

async def get_current_user(payload=Depends(JWTBearer())):
    
    if not isinstance(payload, dict):
        raise HTTPException(status_code=401, detail="Invalid token structure")
    
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")


    return {
        "user_id": user_id
    }
