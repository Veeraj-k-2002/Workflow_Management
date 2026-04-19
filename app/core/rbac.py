from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency import get_current_user
from app.db.session import async_get_db
from app.models.models import User, UserRole


async def get_current_user_with_role(
    user_data: dict = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    """Load current user from DB (authoritative role and company)."""
    result = await db.execute(select(User).where(User.id == user_data["user_id"]))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.id,
        "role": user.role,
        "company_id": user.company_id,
    }


def require_role(*roles: UserRole):
    def role_checker(user_data: dict = Depends(get_current_user_with_role)):
        if user_data["role"] not in roles:
            allowed = ", ".join(r.value for r in roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed}",
            )
        return user_data

    return role_checker


def require_admin():
    return require_role(UserRole.ADMIN)


def require_superuser():
    return require_role(UserRole.SUPERUSER, UserRole.ADMIN)


def require_any_user():
    return require_role(UserRole.NORMAL, UserRole.SUPERUSER, UserRole.ADMIN)
