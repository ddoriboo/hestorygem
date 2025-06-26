from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import io
from typing import Optional, List
from datetime import datetime
from ..db.database import get_db
from ..models.user import User
from ..models.session import Session as UserSession
from ..models.conversation import Conversation
from ..services.autobiography_service import autobiography_service
from .auth import get_current_user

router = APIRouter()

@router.post("/generate")
async def generate_autobiography(
    format: Optional[str] = "text",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """자서전 생성"""
    # 완료된 세션 수 확인
    completed_sessions = db.query(func.count(UserSession.id)).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_completed == True
    ).scalar()
    
    total_conversations = db.query(func.count(Conversation.id)).join(
        UserSession
    ).filter(
        UserSession.user_id == current_user.id
    ).scalar()
    
    if completed_sessions < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"최소 3개 이상의 세션을 완료해야 합니다. 현재 완료: {completed_sessions}개"
        )
    
    if total_conversations < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"더 많은 대화가 필요합니다. 현재 대화 수: {total_conversations}개"
        )
    
    # 모든 대화 데이터 수집
    all_conversations = []
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id
    ).order_by(UserSession.session_number).all()
    
    for session in sessions:
        conversations = db.query(Conversation).filter(
            Conversation.session_id == session.id
        ).order_by(Conversation.created_at).all()
        
        for conv in conversations:
            all_conversations.append({
                "session_number": session.session_number,
                "session_title": session.title,
                "user_message": conv.user_message,
                "ai_response": conv.ai_response,
                "conversation_type": conv.conversation_type,
                "created_at": conv.created_at
            })
    
    # 자서전 생성
    autobiography_text = await autobiography_service.generate_autobiography(
        user_data={
            "id": current_user.id,
            "full_name": current_user.full_name,
            "birth_year": current_user.birth_year
        },
        conversations=all_conversations
    )
    
    if format == "pdf":
        # PDF 생성
        pdf_buffer = await autobiography_service.generate_pdf(
            autobiography_text,
            user_name=current_user.full_name
        )
        
        return StreamingResponse(
            io.BytesIO(pdf_buffer),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=hestory_{current_user.username}.pdf"
            }
        )
    
    return {
        "autobiography": autobiography_text,
        "metadata": {
            "total_sessions": len(sessions),
            "completed_sessions": completed_sessions,
            "total_conversations": total_conversations,
            "generation_date": datetime.now().isoformat()
        }
    }

@router.get("/preview")
async def preview_autobiography(
    session_numbers: Optional[List[int]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 세션들의 자서전 미리보기"""
    query = db.query(UserSession).filter(
        UserSession.user_id == current_user.id
    )
    
    if session_numbers:
        query = query.filter(UserSession.session_number.in_(session_numbers))
    
    sessions = query.order_by(UserSession.session_number).all()
    
    preview_data = []
    for session in sessions:
        conversations = db.query(Conversation).filter(
            Conversation.session_id == session.id
        ).order_by(Conversation.created_at).limit(3).all()
        
        preview_data.append({
            "session_title": session.title,
            "session_number": session.session_number,
            "is_completed": session.is_completed,
            "sample_conversations": [
                {
                    "user": conv.user_message[:100] + "..." if len(conv.user_message) > 100 else conv.user_message,
                    "ai": conv.ai_response[:100] + "..." if len(conv.ai_response) > 100 else conv.ai_response
                }
                for conv in conversations
            ]
        })
    
    return {
        "preview": preview_data,
        "can_generate": len([s for s in sessions if s.is_completed]) >= 3
    }

@router.get("/status")
async def get_autobiography_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """자서전 생성 가능 상태 확인"""
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id
    ).all()
    
    session_stats = []
    total_conversations = 0
    
    for session in sessions:
        conv_count = db.query(func.count(Conversation.id)).filter(
            Conversation.session_id == session.id
        ).scalar()
        
        total_conversations += conv_count
        
        session_stats.append({
            "session_number": session.session_number,
            "title": session.title,
            "is_completed": session.is_completed,
            "conversation_count": conv_count,
            "progress": min(100, (conv_count / 10) * 100)
        })
    
    completed_sessions = sum(1 for s in sessions if s.is_completed)
    can_generate = completed_sessions >= 3 and total_conversations >= 20
    
    return {
        "can_generate": can_generate,
        "requirements": {
            "min_sessions": 3,
            "current_sessions": completed_sessions,
            "min_conversations": 20,
            "current_conversations": total_conversations
        },
        "session_stats": sorted(session_stats, key=lambda x: x["session_number"])
    }