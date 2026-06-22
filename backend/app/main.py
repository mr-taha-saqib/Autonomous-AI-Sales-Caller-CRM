"""FastAPI application entrypoint for the Algorixe AI Sales platform."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text

from app import __version__
from app.api.router import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.logging import configure_logging, get_logger
from app.core.rate_limit import limiter
from app.schemas.common import HealthCheck

configure_logging()
log = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("startup", app=settings.APP_NAME, env=settings.ENVIRONMENT,
             version=__version__)
    yield
    log.info("shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=__version__,
    description="AI-powered cold-calling & CRM platform for Algorixe Car Care.",
    lifespan=lifespan,
)

# --- Middleware ---
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please slow down."},
    )


# --- Routes ---
app.include_router(api_router)


@app.get("/health", response_model=HealthCheck, tags=["system"])
def health():
    db_status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        db_status = f"error: {exc}"
    return HealthCheck(
        status="ok" if db_status == "ok" else "degraded",
        version=__version__,
        database=db_status,
        environment=settings.ENVIRONMENT,
    )


@app.get("/", tags=["system"])
def root():
    return {
        "name": settings.APP_NAME,
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }
