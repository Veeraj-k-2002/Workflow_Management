import uuid
from typing import Any, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import CustomAPIException
from app.models.models import User, UserRole

_USER_UPDATE_FIELDS = frozenset(
    {"name", "email", "country_code", "phone", "year_of_birth", "gender"}
)


def _as_uuid(value: str | uuid.UUID) -> uuid.UUID:
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(str(value))


class RBACService:
    """Role-based access control helpers for users and companies."""

    async def create_user_with_role(
        self,
        db: AsyncSession,
        user_id: str,
        role: UserRole,
        company_id: Optional[str] = None,
    ) -> User:
        user = await db.get(User, _as_uuid(user_id))
        if not user:
            raise CustomAPIException(404, "User not found")

        user.role = role
        if company_id is not None:
            cid = str(company_id).strip()
            user.company_id = _as_uuid(cid) if cid else None
        await db.commit()
        await db.refresh(user)
        return user

    async def get_company_users(
        self,
        db: AsyncSession,
        company_id: str,
        requester_id: str,
        requester_role: UserRole,
    ):
        if requester_role not in (UserRole.ADMIN, UserRole.SUPERUSER):
            raise CustomAPIException(403, "Insufficient permissions")

        requester = await db.get(User, _as_uuid(requester_id))
        if not requester or requester.company_id != _as_uuid(company_id):
            raise CustomAPIException(403, "Cannot access other companies")

        query = select(User).where(User.company_id == _as_uuid(company_id))
        if requester_role == UserRole.SUPERUSER:
            query = query.where(User.role != UserRole.ADMIN)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_users_by_company_id_admin(
        self,
        db: AsyncSession,
        company_id: str,
    ):
        """
        Admin-only: list users for an arbitrary company_id.

        Note: This is intentionally not restricted to the requester's own company,
        because one admin may manage multiple companies.
        """
        try:
            cid = _as_uuid(company_id)
        except ValueError:
            raise CustomAPIException(400, "Invalid company id format")

        result = await db.execute(select(User).where(User.company_id == cid))
        return result.scalars().all()

    async def update_user_data(
        self,
        db: AsyncSession,
        target_user_id: str,
        requester_id: str,
        requester_role: UserRole,
        requester_company_id: Optional[uuid.UUID],
        update_data: dict[str, Any],
    ) -> User:
        target_user = await db.get(User, _as_uuid(target_user_id))
        if not target_user:
            raise CustomAPIException(404, "User not found")

        if requester_role == UserRole.NORMAL:
            if _as_uuid(requester_id) != target_user.id:
                raise CustomAPIException(403, "Cannot update other users' data")

        elif requester_role == UserRole.SUPERUSER:
            if target_user.role == UserRole.ADMIN:
                raise CustomAPIException(403, "Cannot modify admin data")
            if target_user.company_id != requester_company_id:
                raise CustomAPIException(403, "Cannot modify users from other companies")

        elif requester_role == UserRole.ADMIN:
            if target_user.company_id != requester_company_id:
                raise CustomAPIException(403, "Cannot modify users from other companies")

        for key in update_data:
            if key not in _USER_UPDATE_FIELDS:
                raise CustomAPIException(400, f"Cannot update field: {key}")

        for key, value in update_data.items():
            if key == "email" and isinstance(value, str):
                value = value.lower()
            setattr(target_user, key, value)

        await db.commit()
        await db.refresh(target_user)
        return target_user

    async def delete_user(
        self,
        db: AsyncSession,
        target_user_id: str,
        requester_id: str,
        requester_role: UserRole,
        requester_company_id: Optional[uuid.UUID],
    ) -> dict:
        target_user = await db.get(User, _as_uuid(target_user_id))
        if not target_user:
            raise CustomAPIException(404, "User not found")

        if requester_role == UserRole.NORMAL:
            raise CustomAPIException(403, "Cannot delete users")

        if requester_role == UserRole.SUPERUSER:
            if target_user.role == UserRole.ADMIN:
                raise CustomAPIException(403, "Cannot delete admin users")
            if target_user.company_id != requester_company_id:
                raise CustomAPIException(403, "Cannot delete users from other companies")

        if requester_role == UserRole.ADMIN:
            if target_user.company_id != requester_company_id:
                raise CustomAPIException(403, "Cannot delete users from other companies")

        await db.execute(delete(User).where(User.id == target_user.id))
        await db.commit()
        return {"message": "User deleted successfully"}
