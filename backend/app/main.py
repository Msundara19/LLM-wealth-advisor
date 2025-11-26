"""
Main FastAPI application for Wallet Wealth LLM Advisor
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis import init_redis, close_redis
from app.api.v1.router import api_router
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.services.llm import LLMService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown
    """
    # Startup
    logger.info("Starting Wallet Wealth LLM Advisor API")
    
    # Initialize database
    await init_db()
    
    # Initialize Redis
    await init_redis()
    
    # Initialize LLM service
    LLMService.initialize()
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await close_db()
    await close_redis()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Wallet Wealth LLM Advisor API",
    description="AI-powered financial advisory service for Wallet Wealth clients",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*.walletwealth.co.in", "localhost", "127.0.0.1"]
)

# Add custom middleware
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint - API health check
    """
    return {
        "status": "healthy",
        "service": "Wallet Wealth LLM Advisor",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Detailed health check endpoint
    """
    health_status = {
        "status": "healthy",
        "services": {
            "api": "operational",
            "database": "checking",
            "redis": "checking",
            "llm": "checking"
        }
    }
    
    try:
        # Check database connection
        from app.core.database import check_db_health
        db_healthy = await check_db_health()
        health_status["services"]["database"] = "operational" if db_healthy else "degraded"
        
        # Check Redis connection
        from app.core.redis import check_redis_health
        redis_healthy = await check_redis_health()
        health_status["services"]["redis"] = "operational" if redis_healthy else "degraded"
        
        # Check LLM service
        llm_healthy = LLMService.health_check()
        health_status["services"]["llm"] = "operational" if llm_healthy else "degraded"
        
        # Overall status
        if all(status == "operational" for status in health_status["services"].values()):
            health_status["status"] = "healthy"
        elif any(status == "degraded" for status in health_status["services"].values()):
            health_status["status"] = "degraded"
        else:
            health_status["status"] = "unhealthy"
            
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        health_status["status"] = "error"
        health_status["error"] = str(e)
    
    return health_status


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # Don't expose internal errors in production
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal error occurred. Please try again later."}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
