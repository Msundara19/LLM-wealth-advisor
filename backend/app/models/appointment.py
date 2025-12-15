"""
Appointment model for booking consultations
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Boolean
import enum

from app.core.database import Base


class AppointmentStatus(str, enum.Enum):
    """Appointment status options"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Appointment(Base):
    """
    Appointment model for storing consultation bookings
    """
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Client information
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    
    # Appointment details
    service_type = Column(String(100), nullable=False)
    preferred_date = Column(String(20), nullable=False)  # Store as string for flexibility
    preferred_time = Column(String(20), nullable=False)
    message = Column(Text, nullable=True)
    
    # Status tracking
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    admin_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, name={self.name}, status={self.status})>"
