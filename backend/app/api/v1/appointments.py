"""
Appointment API endpoints for booking consultations
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.appointment import Appointment, AppointmentStatus

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/appointments", tags=["appointments"])


# Request/Response Models
class AppointmentCreate(BaseModel):
    """Create appointment request"""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    service_type: str = Field(..., min_length=1, max_length=100)
    preferred_date: str = Field(..., min_length=1)
    preferred_time: str = Field(..., min_length=1)
    message: Optional[str] = None


class AppointmentResponse(BaseModel):
    """Appointment response"""
    id: int
    name: str
    email: str
    phone: str
    service_type: str
    preferred_date: str
    preferred_time: str
    message: Optional[str]
    status: AppointmentStatus
    admin_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AppointmentUpdate(BaseModel):
    """Update appointment (admin)"""
    status: Optional[AppointmentStatus] = None
    admin_notes: Optional[str] = None


class AppointmentPublicResponse(BaseModel):
    """Public response after booking (limited info)"""
    id: int
    message: str
    status: AppointmentStatus


# Public endpoint - anyone can book
@router.post("/book", response_model=AppointmentPublicResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    request: AppointmentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Book a new appointment (public - no auth required)
    """
    try:
        appointment = Appointment(
            name=request.name,
            email=request.email,
            phone=request.phone,
            service_type=request.service_type,
            preferred_date=request.preferred_date,
            preferred_time=request.preferred_time,
            message=request.message,
            status=AppointmentStatus.PENDING
        )
        
        db.add(appointment)
        await db.commit()
        await db.refresh(appointment)
        
        logger.info(f"New appointment booked: {appointment.id} - {appointment.name}")
        
        return AppointmentPublicResponse(
            id=appointment.id,
            message=f"Thank you {request.name}! Your appointment request has been received. We will contact you at {request.phone} to confirm.",
            status=appointment.status
        )
        
    except Exception as e:
        logger.error(f"Error booking appointment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to book appointment. Please try again."
        )


# Admin endpoints - protected with simple token
ADMIN_TOKEN = "wallet-wealth-admin-2024"  # In production, use proper auth


def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple admin verification"""
    if not credentials or credentials.credentials != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin access required"
        )
    return True


@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    status_filter: Optional[AppointmentStatus] = Query(None, alias="status"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    List all appointments (admin only)
    """
    verify_admin(credentials)
    
    try:
        stmt = select(Appointment).order_by(desc(Appointment.created_at))
        
        if status_filter:
            stmt = stmt.where(Appointment.status == status_filter)
        
        stmt = stmt.limit(limit).offset(offset)
        
        result = await db.execute(stmt)
        appointments = result.scalars().all()
        
        return appointments
        
    except Exception as e:
        logger.error(f"Error listing appointments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch appointments"
        )


@router.get("/stats")
async def get_appointment_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Get appointment statistics (admin only)
    """
    verify_admin(credentials)
    
    try:
        # Count by status
        stats = {
            "total": 0,
            "pending": 0,
            "confirmed": 0,
            "completed": 0,
            "cancelled": 0
        }
        
        for status_type in AppointmentStatus:
            stmt = select(Appointment).where(Appointment.status == status_type)
            result = await db.execute(stmt)
            count = len(result.scalars().all())
            stats[status_type.value] = count
            stats["total"] += count
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Get single appointment details (admin only)
    """
    verify_admin(credentials)
    
    stmt = select(Appointment).where(Appointment.id == appointment_id)
    result = await db.execute(stmt)
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    return appointment


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    request: AppointmentUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Update appointment status/notes (admin only)
    """
    verify_admin(credentials)
    
    stmt = select(Appointment).where(Appointment.id == appointment_id)
    result = await db.execute(stmt)
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Update fields
    if request.status is not None:
        appointment.status = request.status
    if request.admin_notes is not None:
        appointment.admin_notes = request.admin_notes
    
    await db.commit()
    await db.refresh(appointment)
    
    logger.info(f"Appointment {appointment_id} updated to status: {appointment.status}")
    
    return appointment


@router.delete("/{appointment_id}")
async def delete_appointment(
    appointment_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an appointment (admin only)
    """
    verify_admin(credentials)
    
    stmt = select(Appointment).where(Appointment.id == appointment_id)
    result = await db.execute(stmt)
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    await db.delete(appointment)
    await db.commit()
    
    logger.info(f"Appointment {appointment_id} deleted")
    
    return {"message": "Appointment deleted successfully"}
