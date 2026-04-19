import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import CustomAPIException
from app.models.models import Company, User


def _as_uuid(value: str | uuid.UUID) -> uuid.UUID:
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(str(value))


def _parse_company_id(value: str | uuid.UUID) -> uuid.UUID:
    try:
        return _as_uuid(value)
    except (ValueError, TypeError):
        raise CustomAPIException(400, "Invalid company id format")


class CompanyService:
    async def create_company(self, db: AsyncSession, name: str) -> Company:
        n = name.strip()
        if not n:
            raise CustomAPIException(400, "Company name cannot be empty")

        dup = await db.execute(select(Company.id).where(Company.name == n))
        if dup.scalar_one_or_none():
            raise CustomAPIException(409, "A company with this name already exists")

        row = Company(name=n)
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row

    async def list_companies(self, db: AsyncSession) -> list[Company]:
        result = await db.execute(select(Company).order_by(Company.name.asc()))
        return list(result.scalars().all())

    async def get_company(self, db: AsyncSession, company_id: str | uuid.UUID) -> Company:
        cid = _parse_company_id(company_id)
        row = await db.get(Company, cid)
        if not row:
            raise CustomAPIException(404, "Company not found")
        return row

    async def update_company(
        self,
        db: AsyncSession,
        company_id: str | uuid.UUID,
        name: str,
    ) -> Company:
        n = name.strip()
        if not n:
            raise CustomAPIException(400, "Company name cannot be empty")

        row = await self.get_company(db, company_id)

        dup = await db.execute(
            select(Company.id).where(Company.name == n, Company.id != row.id)
        )
        if dup.scalar_one_or_none():
            raise CustomAPIException(409, "A company with this name already exists")

        row.name = n
        await db.commit()
        await db.refresh(row)
        return row

    async def delete_company(self, db: AsyncSession, company_id: str | uuid.UUID) -> dict:
        row = await self.get_company(db, company_id)

        in_use = await db.execute(
            select(User.id).where(User.company_id == row.id).limit(1)
        )
        if in_use.scalar_one_or_none():
            raise CustomAPIException(
                409,
                "Cannot delete company while users are assigned to it; reassign or remove users first",
            )

        cid = row.id
        await db.execute(delete(Company).where(Company.id == cid))
        await db.commit()
        return {"message": "Company deleted successfully", "company_id": str(cid)}
