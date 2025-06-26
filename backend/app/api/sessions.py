from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..db.database import get_db
from ..models.user import User
from ..models.session import Session as UserSession
from ..models.conversation import Conversation
from ..schemas.session import Session as SessionSchema, SessionList, SessionUpdate
from ..services.conversation_manager import conversation_manager
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=SessionList)
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자의 모든 세션 조회"""
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id
    ).order_by(UserSession.session_number).all()
    
    # 각 세션의 대화 수 계산
    session_list = []
    for session in sessions:
        conversation_count = db.query(func.count(Conversation.id)).filter(
            Conversation.session_id == session.id
        ).scalar()
        
        session_dict = {
            "id": session.id,
            "user_id": session.user_id,
            "session_number": session.session_number,
            "title": session.title,
            "description": session.description,
            "is_completed": session.is_completed,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "conversation_count": conversation_count
        }
        session_list.append(SessionSchema(**session_dict))
    
    return SessionList(sessions=session_list, total=len(session_list))

@router.get("/{session_id}", response_model=SessionSchema)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 세션 조회"""
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    conversation_count = db.query(func.count(Conversation.id)).filter(
        Conversation.session_id == session.id
    ).scalar()
    
    session_dict = {
        "id": session.id,
        "user_id": session.user_id,
        "session_number": session.session_number,
        "title": session.title,
        "description": session.description,
        "is_completed": session.is_completed,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "conversation_count": conversation_count
    }
    
    return SessionSchema(**session_dict)

@router.patch("/{session_id}", response_model=SessionSchema)
async def update_session(
    session_id: int,
    session_update: SessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """세션 상태 업데이트 (완료 표시 등)"""
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session_update.is_completed is not None:
        session.is_completed = session_update.is_completed
    
    db.commit()
    db.refresh(session)
    
    conversation_count = db.query(func.count(Conversation.id)).filter(
        Conversation.session_id == session.id
    ).scalar()
    
    session_dict = {
        "id": session.id,
        "user_id": session.user_id,
        "session_number": session.session_number,
        "title": session.title,
        "description": session.description,
        "is_completed": session.is_completed,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "conversation_count": conversation_count
    }
    
    return SessionSchema(**session_dict)

@router.get("/{session_id}/progress")
async def get_session_progress(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """세션 진행률 조회"""
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # 대화 수와 대략적인 진행률 계산
    conversation_count = db.query(func.count(Conversation.id)).filter(
        Conversation.session_id == session.id
    ).scalar()
    
    # 총 대화 시간 계산 (오디오 대화의 경우)
    total_duration = db.query(func.sum(Conversation.duration)).filter(
        Conversation.session_id == session.id
    ).scalar() or 0
    
    # 진행률 계산 (대화 10개 이상 또는 30분 이상이면 충분하다고 가정)
    progress = min(100, max(
        (conversation_count / 10) * 100,
        (total_duration / 1800) * 100  # 30분 = 1800초
    ))
    
    return {
        "session_id": session_id,
        "conversation_count": conversation_count,
        "total_duration": total_duration,
        "progress": round(progress, 1),
        "is_completed": session.is_completed
    }

@router.get("/{session_id}/flow-status")
async def get_session_flow_status(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """세션의 대화 흐름 상태 조회"""
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # 대화 관리자에서 진행 상황 가져오기
    flow_progress = conversation_manager.get_session_progress(session_id)
    
    # 세션 템플릿 정보 추가
    from ..models.session_templates import SESSION_TEMPLATES
    session_template = SESSION_TEMPLATES[session.session_number]
    
    return {
        "session_id": session_id,
        "session_number": session.session_number,
        "session_title": session_template["title"],
        "session_objective": session_template["objective"],
        "total_questions": len(session_template["questions"]),
        "current_question_index": flow_progress.get("current_question", 0),
        "next_question": (
            session_template["questions"][flow_progress.get("current_question", 0)]
            if flow_progress.get("current_question", 0) < len(session_template["questions"])
            else None
        ),
        "remaining_questions": len(session_template["questions"]) - flow_progress.get("current_question", 0),
        "flow_progress_percent": flow_progress.get("progress_percent", 0),
        "conversation_count": flow_progress.get("conversation_count", 0),
        "is_flow_completed": flow_progress.get("is_completed", False),
        "all_questions": session_template["questions"]
    }

@router.post("/{session_id}/initialize-flow")
async def initialize_session_flow(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """세션 대화 흐름 초기화"""
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # 대화 관리자에서 세션 초기화
    conversation_manager.initialize_session(session_id, session.session_number)
    
    return {
        "message": "Session flow initialized successfully",
        "session_id": session_id,
        "opening_message": conversation_manager.get_session_opening(session_id)
    }