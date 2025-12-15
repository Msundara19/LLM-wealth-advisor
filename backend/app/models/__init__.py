"""
Models package - exports all SQLAlchemy models
"""

from app.models.user import User, RiskTolerance, InvestmentHorizon
from app.models.chat import ChatSession, ChatMessage, ChatFeedback
from app.models.portfolio import (
    Portfolio, 
    PortfolioHolding, 
    Transaction, 
    AssetType
)
from app.models.appointment import Appointment, AppointmentStatus

__all__ = [
    # User models
    "User",
    "RiskTolerance",
    "InvestmentHorizon",
    
    # Chat models
    "ChatSession",
    "ChatMessage",
    "ChatFeedback",
    
    # Portfolio models
    "Portfolio",
    "PortfolioHolding",
    "Transaction",
    "AssetType",
    
    # Appointment models
    "Appointment",
    "AppointmentStatus",
]
