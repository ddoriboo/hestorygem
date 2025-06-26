from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio
import json
import logging
from ..db.database import get_db
from ..models.user import User
from ..models.session import Session as UserSession
from ..models.conversation import Conversation, ConversationType
from ..schemas.conversation import (
    Conversation as ConversationSchema,
    ConversationList,
    ConversationCreate,
    InterviewRequest,
    InterviewResponse
)
import os
if os.environ.get('RAILWAY_DEPLOYMENT'):
    from ..services.gemini_service_railway import gemini_service
    live_interview_service = None  # Railway에서는 오디오 기능 비활성화
else:
    from ..services.gemini_service import gemini_service
    from ..services.interview_service import live_interview_service
from .auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/session/{session_id}", response_model=ConversationList)
async def get_session_conversations(
    session_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 세션의 모든 대화 조회"""
    # 세션 소유권 확인
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    conversations = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).order_by(Conversation.created_at).offset(skip).limit(limit).all()
    
    total = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).count()
    
    return ConversationList(conversations=conversations, total=total)

@router.post("/interview", response_model=InterviewResponse)
async def create_interview(
    request: InterviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """텍스트 기반 인터뷰 진행"""
    # 세션 확인
    session = db.query(UserSession).filter(
        UserSession.id == request.session_id,
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # 이전 대화 내역 조회
    prev_conversations = db.query(Conversation).filter(
        Conversation.session_id == request.session_id
    ).order_by(Conversation.created_at.desc()).limit(5).all()
    
    conversation_history = [
        {
            "user_message": conv.user_message,
            "ai_response": conv.ai_response
        }
        for conv in reversed(prev_conversations)
    ]
    
    # 세션 시작인지 확인 (첫 번째 대화인지)
    is_session_start = len(prev_conversations) == 0
    
    # AI 응답 생성
    ai_response = await gemini_service.generate_interview_response(
        session_id=request.session_id,
        session_number=session.session_number,
        user_message=request.message,
        conversation_history=conversation_history,
        is_session_start=is_session_start
    )
    
    # 대화 저장
    new_conversation = Conversation(
        session_id=request.session_id,
        conversation_type=ConversationType.TEXT,
        user_message=request.message,
        ai_response=ai_response
    )
    
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    
    return InterviewResponse(
        conversation_id=new_conversation.id,
        ai_response=ai_response
    )

@router.websocket("/live/{session_id}")
async def websocket_live_interview(
    websocket: WebSocket,
    session_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket을 통한 실시간 음성 인터뷰"""
    await websocket.accept()
    
    try:
        # 인증 확인 (WebSocket에서는 헤더로 토큰 전달)
        auth_message = await websocket.receive_json()
        token = auth_message.get("token")
        
        if not token:
            await websocket.close(code=4001, reason="Authentication required")
            return
        
        # 토큰으로 사용자 확인 (실제 구현 시 get_current_user 로직 재사용)
        # 여기서는 간단히 처리
        from .auth import get_current_user, oauth2_scheme
        from fastapi import Request
        
        # 세션 확인
        session = db.query(UserSession).filter(
            UserSession.id == session_id
        ).first()
        
        if not session:
            await websocket.close(code=4004, reason="Session not found")
            return
        
        # Live 인터뷰 시작
        session_key = await live_interview_service.start_live_interview(
            user_id=session.user_id,
            session_id=session_id,
            session_number=session.session_number
        )
        
        # 클라이언트에 준비 완료 메시지 전송
        await websocket.send_json({
            "type": "ready",
            "session_key": session_key
        })
        
        # 메시지 처리 루프
        async def receive_audio():
            while True:
                try:
                    data = await websocket.receive_bytes()
                    await live_interview_service.send_audio_chunk(session_key, data)
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"Error receiving audio: {e}")
                    break
        
        async def send_audio():
            while True:
                try:
                    audio_data = await live_interview_service.get_audio_response(session_key)
                    if audio_data:
                        await websocket.send_bytes(audio_data)
                    
                    # 트랜스크립트도 전송
                    transcript = await live_interview_service.get_transcript(session_key)
                    if transcript:
                        await websocket.send_json({
                            "type": "transcript",
                            "data": transcript
                        })
                    
                    await asyncio.sleep(0.01)
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"Error sending audio: {e}")
                    break
        
        # 동시에 오디오 수신 및 전송
        await asyncio.gather(receive_audio(), send_audio())
        
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=4000, reason=str(e))
    finally:
        # 인터뷰 종료 및 대화 저장
        try:
            result = await live_interview_service.end_live_interview(session_key)
            
            # 대화 내용을 데이터베이스에 저장
            for transcript in result["transcripts"]:
                if transcript["role"] == "user":
                    user_message = transcript["content"]
                    # 다음 assistant 메시지 찾기
                    ai_response = None
                    for next_transcript in result["transcripts"]:
                        if next_transcript["role"] == "assistant":
                            ai_response = next_transcript["content"]
                            break
                    
                    if user_message and ai_response:
                        conversation = Conversation(
                            session_id=session_id,
                            conversation_type=ConversationType.LIVE_AUDIO,
                            user_message=user_message,
                            ai_response=ai_response
                        )
                        db.add(conversation)
            
            db.commit()
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")

@router.post("/generate-autobiography")
async def generate_autobiography(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """전체 대화를 바탕으로 자서전 생성"""
    # 모든 세션의 대화 수집
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
                "created_at": conv.created_at
            })
    
    if len(all_conversations) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough conversations to generate autobiography. Please complete more interview sessions."
        )
    
    # 자서전 생성
    autobiography = await gemini_service.generate_autobiography(
        user_id=current_user.id,
        all_conversations=all_conversations
    )
    
    return {
        "autobiography": autobiography,
        "total_conversations": len(all_conversations),
        "completed_sessions": sum(1 for s in sessions if s.is_completed)
    }