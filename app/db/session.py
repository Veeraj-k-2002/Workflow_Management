from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

USERNAME: str = settings.PG_USERNAME
PASSWORD: str = settings.PG_PASSWORD
HOST: str = settings.PG_HOST
PORT: str = settings.PG_PORT  
DATABASE_NAME: str = settings.DATABASE_NAME

# URL-encode the user and password
encoded_user = quote_plus(USERNAME)
encoded_password = quote_plus(PASSWORD)

# ASYNCRONOUS SETUP
ASYNC_SQLALCHEMY_DATABASE_URI = (
    f"postgresql+asyncpg://{encoded_user}:{encoded_password}@{HOST}:{PORT}/{DATABASE_NAME}"
)
# asyncpg's pooling for higher throughput.
async_engine = create_async_engine(
    ASYNC_SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True
)
async_SessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

async def async_get_db():
    """Dependency to provide an async session in FastAPI routes"""
    db = async_SessionLocal()
    try:
        yield db
    finally:
        await db.close()
