"""Main FastAPI Application for VisionForge AI.

This is the entry point for the VisionForge AI API service.
It sets up the FastAPI application, includes all routers,
and configures middleware, exception handlers, and startup/shutdown events.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time

from .config.settings import get_settings
from .services.llm_service import get_llm_service

# Configure logging
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events for the application.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

    # Initialize services
    try:
        llm_service = get_llm_service()
        # Verify LLM service is healthy
        is_healthy = await llm_service.health_check()
        if is_healthy:
            logger.info(f"LLaM service initialized: {llm_service.get_provider_info()}")
        else:
            logger.warning("LLA_ service initialized but health check failed")
    except Exception as e:
        logger.error(f"Failed to initialize LLM service: {e}")
        # Don't fail startup - allow health checks to report the issue

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI Workflow Engine for generating videos, images, text, and more",
    version=settings.app_version,
    openapi_url=f"/api/v1/openapi.json" if not settings.is_production else None,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware (security)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
    )


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "path": str(request.url)
        }
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for container orchestration and load balancers.

    Returns:
        dict: Basic health status information
    """
    try:
        llm_service = get_llm_service()
        is_healthy = await llm_service.health_check()

        return {
            "status": "healthy" if is_healthy else "degraded",
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "llm_provider": llm_service.get_provider_info().get("provider", "unknown") if llm_service else "not_initialized"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": settings.app_name,
                "error": str(e)
            }
        )


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with basic API information.

    Returns:
        dict: Welcome message and API information
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "api_v1": "/api/v1"
    }


# Include API routers
from .api.routes.llm import router as llm_router
app.include_router(llm_router, prefix="/api/v1", tags=["llm"])

# Additional routers would be included here as they are implemented
# from .api.routes.auth import router as auth_router
# app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
# from .api.routes.users import router as users_router
# app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
# from .api.routes.videos import router as videos_router
# app.include_router(videos_router, prefix="/api/v1/videos", tags=["videos"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=settings.workers if not settings.reload else 1,
        log_level=settings.log_level.lower()
    )