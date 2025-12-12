"""
API v1 Router - aggregates all API endpoints
"""

from fastapi import APIRouter

from app.api.v1.chat import router as chat_router
from app.api.v1.auth import router as auth_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.market import router as market_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(portfolio_router)
api_router.include_router(market_router)
