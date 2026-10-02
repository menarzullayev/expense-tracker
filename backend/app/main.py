import logging
import time
import uuid

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.api import auth, finance
from app.core.config import get_settings
from app.db.session import Base, engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("expense-tracker")
settings = get_settings()

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    if settings.environment != "production":
        Base.metadata.create_all(bind=engine)
    elif settings.jwt_secret == "change-me-in-production":
        raise RuntimeError("JWT_SECRET must be changed before production startup")
    elif len(settings.jwt_secret) < 32:
        raise RuntimeError("JWT_SECRET must be at least 32 characters in production")
    elif settings.database_url.startswith("sqlite"):
        raise RuntimeError("SQLite is not supported for production deployments; use PostgreSQL")
    elif not settings.cors_origin_list:
        raise RuntimeError("CORS_ORIGINS must contain an explicit frontend origin in production")
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", docs_url="/docs", redoc_url="/redoc", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Request-ID"])


@app.middleware("http")
async def request_context(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("unhandled_request_error request_id=%s path=%s", request_id, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal server error", "request_id": request_id})
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    logger.info("request method=%s path=%s status=%s ms=%.1f request_id=%s", request.method, request.url.path, response.status_code, elapsed_ms, request_id)
    return response


@app.get("/health/live", tags=["health"])
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
def readiness() -> dict[str, str]:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT 1")
    return {"status": "ready"}


app.include_router(auth.router, prefix="/v1")
app.include_router(finance.router, prefix="/v1")

