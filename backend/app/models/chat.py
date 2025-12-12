"""
Chat models for storing conversation history
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class ChatSession(Base):
    """
    Chat session model for grouping related messages
    """
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session metadata
    title = Column(String(255), nullable=True)  # Auto-generated from first message
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session")
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id={self.session_id})>"


class ChatMessage(Base):
    """
    Chat message model for storing individual messages
    """
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(36), ForeignKey("chat_sessions.session_id"), nullable=False)
    
    # Message content
    message = Column(Text, nullable=False)      # User's message
    response = Column(Text, nullable=False)     # AI response
    
    # Metadata
    tools_used = Column(Boolean, default=False)
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Context that was used (if any)
    context = Column(JSON, nullable=True)
    
    # Feedback
    feedback_rating = Column(Integer, nullable=True)  # 1-5 rating
    feedback_text = Column(Text, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_messages")
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, user_id={self.user_id})>"


class ChatFeedback(Base):
    """
    Detailed feedback for chat interactions
    """
    __tablename__ = "chat_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Feedback details
    rating = Column(Integer, nullable=False)  # 1-5
    is_helpful = Column(Boolean, nullable=True)
    is_accurate = Column(Boolean, nullable=True)
    feedback_text = Column(Text, nullable=True)
    feedback_category = Column(String(50), nullable=True)  # accuracy, clarity, relevance, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ChatFeedback(id={self.id}, rating={self.rating})>"
