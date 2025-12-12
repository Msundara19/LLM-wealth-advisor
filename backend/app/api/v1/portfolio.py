"""
Portfolio API endpoints
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.portfolio import Portfolio, PortfolioHolding, AssetType
from app.services.portfolio_analyzer import PortfolioAnalyzer

logger = logging.getLogger(__name__)
security = HTTPBearer()

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


# Request/Response Models
class HoldingCreate(BaseModel):
    """Create a new holding"""
    asset_type: AssetType
    symbol: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(..., gt=0)
    average_price: float = Field(..., gt=0)
    purchase_date: Optional[datetime] = None
    notes: Optional[str] = None


class HoldingUpdate(BaseModel):
    """Update a holding"""
    quantity: Optional[float] = Field(None, gt=0)
    average_price: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = None


class HoldingResponse(BaseModel):
    """Holding response"""
    id: int
    asset_type: AssetType
    symbol: str
    name: str
    quantity: float
    average_price: float
    current_price: Optional[float]
    invested_value: float
    current_value: Optional[float]
    unrealized_gain: Optional[float]
    unrealized_gain_pct: Optional[float]
    purchase_date: Optional[datetime]
    notes: Optional[str]
    
    class Config:
        from_attributes = True


class PortfolioCreate(BaseModel):
    """Create a new portfolio"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class PortfolioResponse(BaseModel):
    """Portfolio response"""
    id: int
    name: str
    description: Optional[str]
    total_value: float
    total_invested: float
    total_returns: float
    returns_percentage: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PortfolioDetailResponse(PortfolioResponse):
    """Detailed portfolio response with holdings"""
    holdings: List[HoldingResponse]
    allocation: Optional[dict]
    risk_score: Optional[float]


# Endpoints
@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    request: PortfolioCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new portfolio
    """
    user = await get_current_user(credentials.credentials, db)
    
    portfolio = Portfolio(
        user_id=user.id,
        name=request.name,
        description=request.description
    )
    
    db.add(portfolio)
    await db.commit()
    await db.refresh(portfolio)
    
    logger.info(f"Portfolio created: {portfolio.name} for user {user.id}")
    
    return portfolio


@router.get("/", response_model=List[PortfolioResponse])
async def list_portfolios(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    List all portfolios for current user
    """
    user = await get_current_user(credentials.credentials, db)
    
    stmt = select(Portfolio).where(Portfolio.user_id == user.id)
    result = await db.execute(stmt)
    portfolios = result.scalars().all()
    
    return portfolios


@router.get("/{portfolio_id}", response_model=PortfolioDetailResponse)
async def get_portfolio(
    portfolio_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Get portfolio details with holdings
    """
    user = await get_current_user(credentials.credentials, db)
    
    # Get portfolio
    stmt = select(Portfolio).where(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user.id
    )
    result = await db.execute(stmt)
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    # Get holdings
    stmt = select(PortfolioHolding).where(
        PortfolioHolding.portfolio_id == portfolio_id
    )
    result = await db.execute(stmt)
    holdings = result.scalars().all()
    
    return PortfolioDetailResponse(
        id=portfolio.id,
        name=portfolio.name,
        description=portfolio.description,
        total_value=portfolio.total_value,
        total_invested=portfolio.total_invested,
        total_returns=portfolio.total_returns,
        returns_percentage=portfolio.returns_percentage,
        created_at=portfolio.created_at,
        updated_at=portfolio.updated_at,
        holdings=[HoldingResponse.model_validate(h) for h in holdings],
        allocation=portfolio.allocation,
        risk_score=portfolio.risk_score
    )


@router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a portfolio
    """
    user = await get_current_user(credentials.credentials, db)
    
    stmt = select(Portfolio).where(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user.id
    )
    result = await db.execute(stmt)
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    await db.delete(portfolio)
    await db.commit()
    
    return {"message": "Portfolio deleted successfully"}


# Holdings endpoints
@router.post("/{portfolio_id}/holdings", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
async def add_holding(
    portfolio_id: int,
    request: HoldingCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a new holding to portfolio
    """
    user = await get_current_user(credentials.credentials, db)
    
    # Verify portfolio ownership
    stmt = select(Portfolio).where(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user.id
    )
    result = await db.execute(stmt)
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    # Calculate invested value
    invested_value = request.quantity * request.average_price
    
    holding = PortfolioHolding(
        portfolio_id=portfolio_id,
        asset_type=request.asset_type,
        symbol=request.symbol.upper(),
        name=request.name,
        quantity=request.quantity,
        average_price=request.average_price,
        invested_value=invested_value,
        purchase_date=request.purchase_date,
        notes=request.notes
    )
    
    db.add(holding)
    
    # Update portfolio totals
    portfolio.total_invested += invested_value
    
    await db.commit()
    await db.refresh(holding)
    
    return holding


@router.put("/{portfolio_id}/holdings/{holding_id}", response_model=HoldingResponse)
async def update_holding(
    portfolio_id: int,
    holding_id: int,
    request: HoldingUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a holding
    """
    user = await get_current_user(credentials.credentials, db)
    
    # Verify portfolio ownership
    stmt = select(Portfolio).where(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user.id
    )
    result = await db.execute(stmt)
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    # Get holding
    stmt = select(PortfolioHolding).where(
        PortfolioHolding.id == holding_id,
        PortfolioHolding.portfolio_id == portfolio_id
    )
    result = await db.execute(stmt)
    holding = result.scalar_one_or_none()
    
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holding not found"
        )
    
    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(holding, field, value)
    
    # Recalculate invested value if needed
    if "quantity" in update_data or "average_price" in update_data:
        holding.invested_value = holding.quantity * holding.average_price
    
    await db.commit()
    await db.refresh(holding)
    
    return holding


@router.delete("/{portfolio_id}/holdings/{holding_id}")
async def delete_holding(
    portfolio_id: int,
    holding_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a holding from portfolio
    """
    user = await get_current_user(credentials.credentials, db)
    
    # Verify portfolio ownership
    stmt = select(Portfolio).where(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user.id
    )
    result = await db.execute(stmt)
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    # Get holding
    stmt = select(PortfolioHolding).where(
        PortfolioHolding.id == holding_id,
        PortfolioHolding.portfolio_id == portfolio_id
    )
    result = await db.execute(stmt)
    holding = result.scalar_one_or_none()
    
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holding not found"
        )
    
    # Update portfolio totals
    portfolio.total_invested -= holding.invested_value
    
    await db.delete(holding)
    await db.commit()
    
    return {"message": "Holding deleted successfully"}


# Analysis endpoints
@router.get("/{portfolio_id}/analysis")
async def analyze_portfolio(
    portfolio_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive portfolio analysis
    """
    user = await get_current_user(credentials.credentials, db)
    
    # Get portfolio with holdings
    stmt = select(Portfolio).where(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user.id
    )
    result = await db.execute(stmt)
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    # Get holdings
    stmt = select(PortfolioHolding).where(
        PortfolioHolding.portfolio_id == portfolio_id
    )
    result = await db.execute(stmt)
    holdings = result.scalars().all()
    
    if not holdings:
        return {
            "message": "No holdings in portfolio",
            "portfolio_id": portfolio_id
        }
    
    # Convert to analyzer format
    portfolio_data = {
        "holdings": [
            {
                "symbol": h.symbol,
                "quantity": h.quantity,
                "average_price": h.average_price,
                "asset_type": h.asset_type.value
            }
            for h in holdings
        ]
    }
    
    # Run analysis
    analyzer = PortfolioAnalyzer()
    analysis = analyzer.analyze_portfolio(portfolio_data)
    
    return analysis


@router.post("/{portfolio_id}/refresh-prices")
async def refresh_portfolio_prices(
    portfolio_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh current prices for all holdings
    """
    user = await get_current_user(credentials.credentials, db)
    
    # Get portfolio
    stmt = select(Portfolio).where(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user.id
    )
    result = await db.execute(stmt)
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    # Get holdings
    stmt = select(PortfolioHolding).where(
        PortfolioHolding.portfolio_id == portfolio_id
    )
    result = await db.execute(stmt)
    holdings = result.scalars().all()
    
    from app.services.market_data import MarketDataService
    market_data = MarketDataService()
    
    total_value = 0
    
    for holding in holdings:
        price_data = market_data.get_stock_price(holding.symbol)
        current_price = price_data.get("price", holding.average_price)
        
        holding.current_price = current_price
        holding.current_value = holding.quantity * current_price
        holding.unrealized_gain = holding.current_value - holding.invested_value
        holding.unrealized_gain_pct = (
            (holding.unrealized_gain / holding.invested_value * 100)
            if holding.invested_value > 0 else 0
        )
        
        total_value += holding.current_value
    
    # Update portfolio totals
    portfolio.total_value = total_value
    portfolio.total_returns = total_value - portfolio.total_invested
    portfolio.returns_percentage = (
        (portfolio.total_returns / portfolio.total_invested * 100)
        if portfolio.total_invested > 0 else 0
    )
    
    await db.commit()
    
    return {
        "message": "Prices refreshed successfully",
        "total_value": total_value,
        "total_returns": portfolio.total_returns,
        "returns_percentage": portfolio.returns_percentage
    }
