"""
Portfolio models for storing user investment portfolios
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class AssetType(str, enum.Enum):
    """Types of assets"""
    STOCK = "stock"
    MUTUAL_FUND = "mutual_fund"
    ETF = "etf"
    BOND = "bond"
    FD = "fixed_deposit"
    GOLD = "gold"
    REAL_ESTATE = "real_estate"
    CRYPTO = "crypto"
    OTHER = "other"


class Portfolio(Base):
    """
    User portfolio model
    """
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Portfolio info
    name = Column(String(255), nullable=False, default="My Portfolio")
    description = Column(Text, nullable=True)
    
    # Calculated values (updated periodically)
    total_value = Column(Float, default=0.0)
    total_invested = Column(Float, default=0.0)
    total_returns = Column(Float, default=0.0)
    returns_percentage = Column(Float, default=0.0)
    
    # Risk metrics
    risk_score = Column(Float, nullable=True)  # 1-10
    volatility = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    
    # Asset allocation (JSON: {"stocks": 60, "bonds": 30, "cash": 10})
    allocation = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("PortfolioHolding", back_populates="portfolio")
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, name={self.name})>"


class PortfolioHolding(Base):
    """
    Individual holdings within a portfolio
    """
    __tablename__ = "portfolio_holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    
    # Asset identification
    asset_type = Column(Enum(AssetType), nullable=False)
    symbol = Column(String(50), nullable=False)  # e.g., RELIANCE.NS, HDFC0001234
    name = Column(String(255), nullable=False)
    
    # Holding details
    quantity = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    
    # Calculated values
    invested_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=True)
    unrealized_gain = Column(Float, nullable=True)
    unrealized_gain_pct = Column(Float, nullable=True)
    
    # Additional info
    purchase_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    
    def __repr__(self):
        return f"<PortfolioHolding(id={self.id}, symbol={self.symbol})>"


class Transaction(Base):
    """
    Transaction history for portfolio
    """
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    holding_id = Column(Integer, ForeignKey("portfolio_holdings.id"), nullable=True)
    
    # Transaction details
    transaction_type = Column(String(20), nullable=False)  # BUY, SELL, DIVIDEND, SPLIT
    symbol = Column(String(50), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Fees and taxes
    brokerage = Column(Float, default=0.0)
    taxes = Column(Float, default=0.0)
    other_charges = Column(Float, default=0.0)
    
    # Timestamps
    transaction_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type}, symbol={self.symbol})>"
