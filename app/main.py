from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router.v1 import auth_router, rbac_router, task_router
from contextlib import asynccontextmanager
from sqlalchemy import text
from app.db.session import async_engine
from app.models.models import Base
from app.core.config import settings
import logging


logger = logging.getLogger(__name__)


async def _ensure_rbac_columns(conn):
    """
    Older databases may have task.users from before role/company_id existed.
    create_all() does not ALTER existing tables, so apply additive DDL here.
    """
    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS task.companies (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR NOT NULL UNIQUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )
    )
    await conn.execute(
        text(
            """
            ALTER TABLE task.users
            ADD COLUMN IF NOT EXISTS role VARCHAR(32) NOT NULL DEFAULT 'normal';
            """
        )
    )
    await conn.execute(
        text(
            """
            ALTER TABLE task.users
            ADD COLUMN IF NOT EXISTS company_id UUID;
            """
        )
    )
    await conn.execute(
        text(
            """
            ALTER TABLE task.tasks
            ADD COLUMN IF NOT EXISTS started_at TIMESTAMPTZ,
            ADD COLUMN IF NOT EXISTS review_due_at TIMESTAMPTZ,
            ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMPTZ,
            ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ,
            ADD COLUMN IF NOT EXISTS done_at TIMESTAMPTZ;
            """
        )
    )



@asynccontextmanager
async def lifespan(app: FastAPI):
    try:

        # --- Startup: DB schema / extension ---
        async with async_engine.connect() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS task"))
            await conn.commit()

        # --- Startup: create tables ---
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await _ensure_rbac_columns(conn)

        logger.info("Tables created successfully")

        # Hand control to the app
        yield

    finally:
        # --- Shutdown: close resources ---
        await async_engine.dispose()  # close pools/connections



app = FastAPI(
    title="Multi Tenant Workflow Platform",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:50684",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the auth routes under the /api/v1 prefix
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(task_router.router, prefix="/api/v1")
app.include_router(rbac_router.router, prefix="/api/v1")