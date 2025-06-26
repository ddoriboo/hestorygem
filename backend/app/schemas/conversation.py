from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ConversationType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    LIVE_AUDIO = "live_audio"

class ConversationBase(BaseModel):
    conversation_type: ConversationType
    user_message: Optional[str] = None
    ai_response: Optional[str] = None

class ConversationCreate(ConversationBase):
    session_id: int
    audio_url: Optional[str] = None
    duration: Optional[int] = None

class ConversationInDB(ConversationBase):
    id: int
    session_id: int
    audio_url: Optional[str] = None
    duration: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class Conversation(ConversationInDB):
    pass

class ConversationList(BaseModel):
    conversations: List[Conversation]
    total: int

class InterviewRequest(BaseModel):
    session_number: int  # 웹앱에서 사용하는 필드명
    user_message: str    # 웹앱에서 사용하는 필드명
    is_session_start: bool = False
    conversation_type: ConversationType = ConversationType.TEXT

class InterviewResponse(BaseModel):
    conversation_id: int
    ai_response: str
    audio_url: Optional[str] = None