"""
Uber Eats API - Main application module
"""
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_client import make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.metrics import MetricsMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    print("Starting Uber Eats API...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    print("Shutting down Uber Eats API...")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan,
        description="""
        ## Uber Eats API Integration
        
        This API provides integration with Uber Eats marketplace APIs for:
        - Store management
        - Menu synchronization
        - Order processing
        - Webhook handling
        
        ### Authentication
        
        All endpoints require OAuth2 authentication using Uber Eats client credentials.
        
        ### Rate Limiting
        
        API requests are rate limited according to Uber Eats guidelines.
        """,
    )
    
    # Add middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(MetricsMiddleware)
    
    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Mount metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root() -> Dict[str, Any]:
        """Root endpoint"""
        return {
            "message": "Welcome to Uber Eats API",
            "version": settings.VERSION,
            "docs_url": f"{settings.API_V1_STR}/docs",
            "health_url": f"{settings.API_V1_STR}/health",
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check() -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
        }
    
    return app


app = create_application()