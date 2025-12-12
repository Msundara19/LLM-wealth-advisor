"""
User model for authentication and profile management
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class RiskTolerance(str, enum.Enum):
    """User risk tolerance levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class InvestmentHorizon(str, enum.Enum):
    """Investment time horizon"""
    SHORT = "short"      # < 3 years
    MEDIUM = "medium"    # 3-7 years
    LONG = "long"        # > 7 years


class User(Base):
    """
    User model for storing user information and preferences
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)
    
    # Financial profile
    risk_tolerance = Column(
        Enum(RiskTolerance), 
        default=RiskTolerance.MODERATE,
        nullable=True
    )
    investment_horizon = Column(
        Enum(InvestmentHorizon),
        default=InvestmentHorizon.MEDIUM,
        nullable=True
    )
    monthly_income = Column(Integer, nullable=True)  # In INR
    investment_goals = Column(Text, nullable=True)   # JSON string of goals
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    chat_messages = relationship("ChatMessage", back_populates="user")
    portfolios = relationship("Portfolio", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
    
    @property
    def display_name(self) -> str:
        """Get display name for user"""
        return self.full_name or self.email.split("@")[0]
