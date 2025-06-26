from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .user import Base
import enum

class ConversationType(str, enum.Enum):
    TEXT = "text"
    AUDIO = "audio"
    LIVE_AUDIO = "live_audio"

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    conversation_type = Column(Enum(ConversationType), nullable=False)
    user_message = Column(Text)
    ai_response = Column(Text)
    audio_url = Column(String)  # S3 URL for audio files
    duration = Column(Integer)  # Duration in seconds for audio
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="conversations")