from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SessionBase(BaseModel):
    session_number: int
    title: str
    description: Optional[str] = None

class SessionCreate(SessionBase):
    user_id: int

class SessionUpdate(BaseModel):
    is_completed: Optional[bool] = None

class SessionInDB(SessionBase):
    id: int
    user_id: int
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Session(SessionInDB):
    conversation_count: Optional[int] = 0

class SessionList(BaseModel):
    sessions: List[Session]
    total: int