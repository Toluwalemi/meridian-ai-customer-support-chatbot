from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from apps.chat.urls import limiter as chat_limiter
from apps.chat.urls import router as chat_router
from apps.mcp.services import mcp_service
from apps.mcp.urls import router as mcp_router
from core.exceptions import register_exception_handlers
from core.logging import configure_logging, logger
from core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging(settings.debug)
    try:
        await mcp_service.connect()
    except Exception as exc:
        logger.error("startup.mcp_connect_failed", error=str(exc))
    yield
    await mcp_service.close()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

    app.state.limiter = chat_limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    register_exception_handlers(app)

    @app.get("/healthz", tags=["meta"])
    async def healthz() -> dict[str, str]:
        return {"status": "ok", "env": settings.env}

    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(mcp_router, prefix="/api/v1")

    return app


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    del request
    return JSONResponse(status_code=429, content={"detail": f"Rate limit exceeded: {exc.detail}"})


app = create_app()
