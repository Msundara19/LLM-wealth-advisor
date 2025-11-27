"""
Chat API endpoints for the LLM Advisor
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from app.services.llm import llm_service
from app.core.auth import get_current_user
from app.models.chat import ChatMessage
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
security = HTTPBearer()

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    session_id: str
    timestamp: datetime
    tools_used: bool = False


class PortfolioAnalysisRequest(BaseModel):
    """Portfolio analysis request"""
    portfolio_data: Dict[str, Any]
    analysis_type: str = "comprehensive"


class InvestmentRecommendationRequest(BaseModel):
    """Investment recommendation request"""
    age: int = Field(..., ge=18, le=100)
    risk_tolerance: str = Field(...,
                                pattern="^(conservative|moderate|aggressive)$")
    investment_horizon: str = Field(..., pattern="^(short|medium|long)$")
    monthly_income: float = Field(..., gt=0)
    goals: list[str]
    current_investments: Optional[Dict[str, Any]] = None


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to the LLM advisor and get a response
    """
    try:
        # Verify user authentication
        user = await get_current_user(credentials.credentials, db)

        # Process the message
        result = await llm_service.process_message(
            user_id=str(user.id),
            message=request.message,
            context=request.context
        )

        # Store message in database
        chat_message = ChatMessage(
            user_id=user.id,
            session_id=request.session_id or generate_session_id(),
            message=request.message,
            response=result["response"],
            timestamp=datetime.utcnow()
        )
        db.add(chat_message)
        await db.commit()

        return ChatResponse(
            response=result["response"],
            session_id=chat_message.session_id,
            timestamp=result["timestamp"],
            tools_used=result.get("tools_used", False)
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process message")


@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time chat
    """
    await websocket.accept()
    logger.info(f"WebSocket connection established for session {session_id}")

    try:
        # Authenticate user from query params or first message
        auth_message = await websocket.receive_json()
        token = auth_message.get("token")

        if not token:
            await websocket.send_json({"error": "Authentication required"})
            await websocket.close()
            return

        user = await get_current_user(token, db)

        await websocket.send_json({
            "type": "auth_success",
            "message": "Authentication successful"
        })

        # Chat loop
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = data.get("message")

            if not message:
                continue

            # Send typing indicator
            await websocket.send_json({
                "type": "typing",
                "status": "start"
            })

            # Process message
            result = await llm_service.process_message(
                user_id=str(user.id),
                message=message,
                context=data.get("context")
            )

            # Send response
            await websocket.send_json({
                "type": "message",
                "response": result["response"],
                "timestamp": result["timestamp"],
                "tools_used": result.get("tools_used", False)
            })

            # Stop typing indicator
            await websocket.send_json({
                "type": "typing",
                "status": "stop"
            })

            # Store in database
            chat_message = ChatMessage(
                user_id=user.id,
                session_id=session_id,
                message=message,
                response=result["response"],
                timestamp=datetime.utcnow()
            )
            db.add(chat_message)
            await db.commit()

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        await websocket.send_json({"error": str(e)})
        await websocket.close()


@router.post("/portfolio-analysis")
async def analyze_portfolio(
    request: PortfolioAnalysisRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a comprehensive portfolio analysis report
    """
    try:
        user = await get_current_user(credentials.credentials, db)

        report = await llm_service.generate_portfolio_report(
            user_id=str(user.id),
            portfolio_data=request.portfolio_data
        )

        return {
            "report": report,
            "generated_at": datetime.utcnow().isoformat(),
            "analysis_type": request.analysis_type
        }

    except Exception as e:
        logger.error(f"Portfolio analysis error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze portfolio")


@router.post("/investment-recommendations")
async def get_investment_recommendations(
    request: InvestmentRecommendationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized investment recommendations
    """
    try:
        await get_current_user(credentials.credentials, db)

        user_profile = request.dict()
        recommendations = await llm_service.get_investment_recommendation(user_profile)

        return recommendations

    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500,
                            detail="Failed to generate recommendations")


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    limit: int = 50
):
    """
    Get chat history for a session
    """
    try:
        user = await get_current_user(credentials.credentials, db)

        # Query chat messages from database
        from sqlalchemy import select
        stmt = select(ChatMessage).where(
            ChatMessage.session_id == session_id,
            ChatMessage.user_id == user.id
        ).order_by(ChatMessage.timestamp.desc()).limit(limit)

        result = await db.execute(stmt)
        messages = result.scalars().all()

        return {
            "session_id": session_id,
            "messages": [
                {
                    "message": msg.message,
                    "response": msg.response,
                    "timestamp": msg.timestamp
                }
                for msg in reversed(messages)
            ]
        }

    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve history")


@router.delete("/clear-memory")
async def clear_memory(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Clear the conversation memory for the current user
    """
    try:
        user = await get_current_user(credentials.credentials, db)
        llm_service.clear_user_memory(str(user.id))

        return {"message": "Conversation memory cleared successfully"}

    except Exception as e:
        logger.error(f"Memory clear error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to clear memory")


def generate_session_id() -> str:
    """Generate a unique session ID"""
    import uuid
    return str(uuid.uuid4())
