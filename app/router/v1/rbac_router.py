import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import CustomAPIException
from app.core.rbac import require_admin, require_superuser
from app.db.session import async_get_db
from app.models.models import UserRole
from app.services.company_service import CompanyService
from app.services.rbac_service import RBACService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin RBAC"])
rbac_service = RBACService()
company_service = CompanyService()


class AssignRoleRequest(BaseModel):
    user_id: str
    role: UserRole
    company_id: Optional[str] = None


class UserListResponse(BaseModel):
    user_id: str
    name: str
    email: str
    role: UserRole


class CompanyUsersResponse(BaseModel):
    users: List[UserListResponse]
    count: int


class CompanyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)


class CompanyUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1)


class CompanyResponse(BaseModel):
    company_id: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    companies: List[CompanyResponse]
    count: int


@router.post("/companies", response_model=CompanyResponse)
async def create_company_api(
    body: CompanyCreateRequest,
    _admin: dict = Depends(require_admin()),
    db: AsyncSession = Depends(async_get_db),
):
    """Admin only: create a company."""
    try:
        row = await company_service.create_company(db, body.name)
        return CompanyResponse(
            company_id=str(row.id),
            name=row.name,
            created_at=row.created_at,
        )
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        await db.rollback()
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies", response_model=CompanyListResponse)
async def list_companies_api(
    _admin: dict = Depends(require_admin()),
    db: AsyncSession = Depends(async_get_db),
):
    """Admin only: list all companies."""
    try:
        rows = await company_service.list_companies(db)
        return CompanyListResponse(
            companies=[
                CompanyResponse(
                    company_id=str(c.id),
                    name=c.name,
                    created_at=c.created_at,
                )
                for c in rows
            ],
            count=len(rows),
        )
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company_api(
    company_id: str,
    _admin: dict = Depends(require_admin()),
    db: AsyncSession = Depends(async_get_db),
):
    """Admin only: get one company by id."""
    try:
        row = await company_service.get_company(db, company_id)
        return CompanyResponse(
            company_id=str(row.id),
            name=row.name,
            created_at=row.created_at,
        )
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def update_company_api(
    company_id: str,
    body: CompanyUpdateRequest,
    _admin: dict = Depends(require_admin()),
    db: AsyncSession = Depends(async_get_db),
):
    """Admin only: update company name."""
    try:
        row = await company_service.update_company(db, company_id, body.name)
        return CompanyResponse(
            company_id=str(row.id),
            name=row.name,
            created_at=row.created_at,
        )
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        await db.rollback()
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/companies/{company_id}", response_model=dict)
async def delete_company_api(
    company_id: str,
    _admin: dict = Depends(require_admin()),
    db: AsyncSession = Depends(async_get_db),
):
    """Admin only: delete a company (blocked if any user is assigned)."""
    try:
        return await company_service.delete_company(db, company_id)
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        await db.rollback()
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assign_role", response_model=dict)
async def assign_role_api(
    request: AssignRoleRequest,
    user_data: dict = Depends(require_admin()),
    db: AsyncSession = Depends(async_get_db),
):
    """Admin only: assign role (and optional company) to a user."""
    try:
        cid = request.company_id
        if cid is None and user_data.get("company_id") is not None:
            cid = str(user_data["company_id"])
        result = await rbac_service.create_user_with_role(
            db, request.user_id, request.role, cid
        )
        return {"message": "Role assigned successfully", "user_id": str(result.id)}
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        await db.rollback()
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/company_users", response_model=CompanyUsersResponse)
async def get_company_users_api(
    user_data: dict = Depends(require_superuser()),
    db: AsyncSession = Depends(async_get_db),
):
    """Superuser and admin: list users in the requester's company."""
    try:
        cid = user_data.get("company_id")
        if cid is None:
            raise CustomAPIException(
                400,
                "User has no company assigned. Admins: set your company via POST /api/v1/admin/assign_role "
                "(same user_id, desired role, company_id) or create a new company with POST /api/v1/admin/companies "
                "(the creator is linked automatically if they had no company).",
            )

        users = await rbac_service.get_company_users(
            db,
            str(cid),
            str(user_data["user_id"]),
            user_data["role"],
        )
        return CompanyUsersResponse(
            users=[
                UserListResponse(
                    user_id=str(u.id),
                    name=u.name,
                    email=u.email,
                    role=u.role,
                )
                for u in users
            ],
            count=len(users),
        )
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies/{company_id}/users", response_model=CompanyUsersResponse)
async def get_company_users_by_company_id_api(
    company_id: str,
    _admin: dict = Depends(require_admin()),
    db: AsyncSession = Depends(async_get_db),
):
    """Admin only: list users for the given company_id."""
    try:
        users = await rbac_service.get_users_by_company_id_admin(db, company_id)
        return CompanyUsersResponse(
            users=[
                UserListResponse(
                    user_id=str(u.id),
                    name=u.name,
                    email=u.email,
                    role=u.role,
                )
                for u in users
            ],
            count=len(users),
        )
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update_user/{user_id}", response_model=dict)
async def update_user_api(
    user_id: str,
    update_data: dict = Body(...),
    user_data: dict = Depends(require_superuser()),
    db: AsyncSession = Depends(async_get_db),
):
    """Superuser and admin: update allowed profile fields for a user."""
    try:
        result = await rbac_service.update_user_data(
            db,
            user_id,
            str(user_data["user_id"]),
            user_data["role"],
            user_data["company_id"],
            update_data,
        )
        return {"message": "User updated successfully", "user_id": str(result.id)}
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        await db.rollback()
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete_user/{user_id}", response_model=dict)
async def delete_user_api(
    user_id: str,
    user_data: dict = Depends(require_admin()),
    db: AsyncSession = Depends(async_get_db),
):
    """Admin only: delete a user in the same company."""
    try:
        return await rbac_service.delete_user(
            db,
            user_id,
            str(user_data["user_id"]),
            user_data["role"],
            user_data["company_id"],
        )
    except CustomAPIException as e:
        logger.error("CustomError: %s", e.detail)
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        await db.rollback()
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(e))
