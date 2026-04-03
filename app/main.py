from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router.v1 import auth_router,task_router
from contextlib import asynccontextmanager
from sqlalchemy import text
from app.db.session import async_engine
from app.models.models import Base
from app.core.config import settings
import logging


logger = logging.getLogger(__name__)

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

        logger.info("Tables created successfully")

        # Hand control to the app
        yield

    finally:
        # --- Shutdown: close resources ---
        await async_engine.dispose()  # close pools/connections



app = FastAPI(
    title="Task Assignment",
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