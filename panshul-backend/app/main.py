"""App entrypoint. Routes are thin; all logic lives in services/agents."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import new_request_id, setup_logging
from app.db.base import Base
from app.db.session import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.debug)
    if settings.env == "development":
        # Dev convenience only — use Alembic migrations in production.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    logger.info("startup complete env=%s", settings.env)
    yield
    await engine.dispose()


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan,
              docs_url="/docs", openapi_url="/openapi.json")

def _cors_origins() -> list[str]:
    if settings.env.strip().lower() == "production" and settings.debug:
        raise RuntimeError("DEBUG must be false when ENV=production")
    if settings.debug:
        return ["*"]
    origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    if "*" in origins:
        raise RuntimeError("CORS_ORIGINS cannot contain '*' when DEBUG=false")
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    rid = new_request_id()
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code,
                        content={"error": exc.code, "message": exc.message})


@app.get("/health", tags=["ops"])
async def health():
    return {"status": "ok", "env": settings.env}


app.include_router(api_router, prefix=settings.api_v1_prefix)
