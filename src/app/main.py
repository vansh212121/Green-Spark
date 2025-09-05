from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from typing import Dict, Any

from src.app.core.config import settings
from src.app.core.exception_handler import register_exception_handlers
from src.app.core.middleware import register_middlewares
from src.app.db.session import db
from src.app.utils.deps import get_health_status
from src.app.api.v1.endpoints import user, auth, admin, bill, appliance, insights
from src.app.db import base

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    # Startup: Connect to the database
    await db.connect()

    yield

    # Shutdown: Disconnect from the database
    await db.disconnect()


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        lifespan=lifespan,
    )

    # Register all middleware
    register_middlewares(app)

    # Register all exception handlers
    register_exception_handlers(app)

    # Include your routers here later
    app.include_router(auth.router)
    app.include_router(user.router)
    app.include_router(admin.router)
    app.include_router(bill.router)
    app.include_router(appliance.router)
    app.include_router(insights.router)

    return app


app = create_application()


@app.get("/health", response_model=Dict[str, Any])
async def health_check(health: Dict[str, Any] = Depends(get_health_status)):
    """
    Health check endpoint that provides status and version info.
    """
    return health
