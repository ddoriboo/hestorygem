#!/usr/bin/env python3
"""
He'story 인터뷰 시스템 테스트 스크립트
"""

import asyncio
import sys
import os

# 프로젝트 루트를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.gemini_service import gemini_service
from app.services.conversation_manager import conversation_manager
from app.models.session_templates import SESSION_TEMPLATES

async def test_interview_flow():
    """인터뷰 흐름 테스트"""
    print("=== He'story 인터뷰 시스템 테스트 ===\n")
    
    # 테스트 세션 설정
    test_session_id = 1
    test_session_number = 0  # 프롤로그
    
    print(f"테스트 세션: {SESSION_TEMPLATES[test_session_number]['title']}\n")
    
    # 세션 시작
    print("1. 세션 시작...")
    opening = await gemini_service.generate_interview_response(
        session_id=test_session_id,
        session_number=test_session_number,
        user_message="",
        is_session_start=True
    )
    print(f"AI: {opening}\n")
    
    # 사용자 응답 시뮬레이션
    user_responses = [
        "네, 시작하겠습니다.",
        "저는 경상남도 진주에서 태어났습니다. 할아버지 때부터 그곳에서 살았어요.",
        "할아버지는 농사를 지으셨고, 할머니는 집안일을 하셨어요. 아주 엄격하신 분들이셨죠.",
        "제가 태어날 무렵은 일제강점기였습니다. 참 어려운 시절이었어요.",
        "형제는 3남 2녀였습니다. 제가 둘째였어요."
    ]
    
    print("2. 대화 진행...")
    for i, user_input in enumerate(user_responses):
        print(f"사용자: {user_input}")
        
        # AI 응답 생성
        ai_response = await gemini_service.generate_interview_response(
            session_id=test_session_id,
            session_number=test_session_number,
            user_message=user_input,
            conversation_history=[],
            is_session_start=False
        )
        
        print(f"AI: {ai_response}\n")
        
        # 진행 상황 확인
        progress = conversation_manager.get_session_progress(test_session_id)
        print(f"[진행률: {progress.get('progress_percent', 0):.1f}%]\n")
        
        await asyncio.sleep(1)  # 시뮬레이션을 위한 대기
    
    print("3. 세션 완료 상태 확인...")
    is_completed = conversation_manager.is_session_completed(test_session_id)
    print(f"세션 완료: {is_completed}")
    
    print("\n=== 테스트 완료 ===")

async def test_conversation_manager():
    """대화 관리자 단독 테스트"""
    print("=== 대화 관리자 테스트 ===\n")
    
    test_session_id = 999
    test_session_number = 1  # 유년 시절
    
    # 세션 초기화
    print("1. 세션 초기화...")
    conversation_manager.initialize_session(test_session_id, test_session_number)
    
    # 세션 시작 메시지
    opening = conversation_manager.get_session_opening(test_session_id)
    print(f"시작 메시지: {opening}\n")
    
    # 질문 진행
    print("2. 질문 진행 테스트...")
    for i in range(3):
        question = conversation_manager.get_next_question(test_session_id)
        if question:
            print(f"질문 {i+1}: {question}")
            
            # 꼬리 질문 테스트
            follow_up = conversation_manager.generate_follow_up_question(
                test_session_id, 
                "저는 어릴 때 시골에서 살았어요."
            )
            print(f"꼬리 질문: {follow_up}\n")
        
        # 진행 상황
        progress = conversation_manager.get_session_progress(test_session_id)
        print(f"진행률: {progress.get('progress_percent', 0):.1f}%\n")
    
    print("=== 대화 관리자 테스트 완료 ===")

def print_session_templates():
    """세션 템플릿 정보 출력"""
    print("=== 12개 세션 템플릿 ===\n")
    
    for template in SESSION_TEMPLATES:
        print(f"세션 {template['session_number']}: {template['title']}")
        print(f"목표: {template['objective']}")
        print(f"질문 수: {len(template['questions'])}개")
        print("주요 질문들:")
        for i, question in enumerate(template['questions'][:3]):
            print(f"  {i+1}. {question}")
        if len(template['questions']) > 3:
            print(f"  ... 외 {len(template['questions']) - 3}개")
        print()

async def main():
    """메인 테스트 함수"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "templates":
            print_session_templates()
        elif test_type == "manager":
            await test_conversation_manager()
        elif test_type == "full":
            await test_interview_flow()
        else:
            print("사용법: python test_interview.py [templates|manager|full]")
    else:
        print("간단한 테스트를 실행합니다...")
        print_session_templates()
        print("\n" + "="*50 + "\n")
        await test_conversation_manager()

if __name__ == "__main__":
    asyncio.run(main())