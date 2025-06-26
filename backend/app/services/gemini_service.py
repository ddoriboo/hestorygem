import asyncio
import base64
import io
import os
from typing import Optional, AsyncGenerator
import pyaudio
from google import genai
from ..config import settings
from ..models.session_templates import SESSION_TEMPLATES, MEMORY_GUIDE_SYSTEM_PROMPT
from .conversation_manager import conversation_manager

class GeminiService:
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.google_api_key,
            http_options={"api_version": "v1beta"}
        )
        self.pya = pyaudio.PyAudio()
        
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """일반적인 텍스트 생성"""
        model = self.client.models.get(settings.gemini_model)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await model.generate_content_async(messages)
        return response.text
    
    async def generate_interview_response(
        self, 
        session_id: int,
        session_number: int, 
        user_message: str,
        conversation_history: list = [],
        is_session_start: bool = False
    ) -> str:
        """인터뷰 응답 생성 (개선된 버전)"""
        session_template = SESSION_TEMPLATES[session_number]
        
        # 세션이 시작된 적이 없다면 초기화
        if is_session_start:
            conversation_manager.initialize_session(session_id, session_number)
            return conversation_manager.get_session_opening(session_id)
        
        # 대화 수 업데이트
        conversation_manager.update_conversation_count(session_id)
        
        # 사용자 응답이 있는 경우 (첫 인사가 아닌 경우)
        if user_message and user_message.strip():
            # 꼬리 질문이 필요한지 판단
            if conversation_manager.should_ask_follow_up(session_id, user_message):
                follow_up = conversation_manager.generate_follow_up_question(session_id, user_message)
                if follow_up:
                    # 공감 표현과 함께 꼬리 질문
                    empathy_responses = [
                        "정말 소중한 이야기네요.",
                        "그런 경험이 있으셨군요.",
                        "말씀해주셔서 감사합니다.",
                        "아, 그러셨구나.",
                        "정말 인상 깊은 이야기입니다."
                    ]
                    import random
                    empathy = random.choice(empathy_responses)
                    return f"{empathy} {follow_up}"
            
            # 다음 주요 질문으로 넘어갈 시점인지 확인
            elif conversation_manager.can_move_to_next_question(session_id):
                next_question = conversation_manager.get_next_question(session_id)
                if next_question:
                    return f"이제 다음 이야기로 넘어가 봐도 괜찮을까요? {next_question}"
                else:
                    # 세션 완료
                    next_session_number = session_number + 1
                    next_session_title = None
                    if next_session_number < len(SESSION_TEMPLATES):
                        next_session_title = SESSION_TEMPLATES[next_session_number]["title"]
                    
                    return conversation_manager.get_session_closure(session_id, next_session_title)
        
        # 첫 질문 제시 (사용자가 "시작하겠습니다" 등으로 응답한 경우)
        first_question = conversation_manager.get_next_question(session_id)
        if first_question:
            return first_question
        
        # AI 백업 응답 (복잡한 상황 처리)
        return await self.generate_contextual_response(
            session_number, user_message, conversation_history
        )
    
    async def generate_contextual_response(
        self,
        session_number: int,
        user_message: str,
        conversation_history: list = []
    ) -> str:
        """맥락적 응답 생성 (백업 메서드)"""
        session_template = SESSION_TEMPLATES[session_number]
        
        system_prompt = f"""{MEMORY_GUIDE_SYSTEM_PROMPT}

현재 세션: {session_template['title']}
세션 목표: {session_template['objective']}

현재 사용자가 말씀하신 내용에 대해 '기억의 안내자'로서 적절한 응답을 해주세요."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 최근 대화 히스토리 추가
        for conv in conversation_history[-3:]:
            if conv.get("user_message"):
                messages.append({"role": "user", "content": conv.get("user_message", "")})
            if conv.get("ai_response"):
                messages.append({"role": "assistant", "content": conv.get("ai_response", "")})
        
        messages.append({"role": "user", "content": user_message})
        
        model = self.client.models.get(settings.gemini_model)
        response = await model.generate_content_async(messages)
        return response.text
    
    async def generate_autobiography(self, user_id: int, all_conversations: list) -> str:
        """전체 대화를 바탕으로 자서전 생성"""
        system_prompt = """당신은 전문적인 자서전 작가입니다.
주어진 인터뷰 내용을 바탕으로 감동적이고 잘 구성된 자서전을 작성해주세요.

지침:
1. 1인칭 시점으로 작성하세요
2. 시간 순서대로 구성하되, 자연스러운 흐름을 유지하세요
3. 구체적인 에피소드와 감정을 생생하게 표현하세요
4. 각 장은 SESSION_TEMPLATES의 제목을 사용하세요
5. 전체 분량은 A4 30-50페이지 정도로 작성하세요"""
        
        # 모든 대화를 정리
        organized_content = self._organize_conversations(all_conversations)
        
        prompt = f"다음 인터뷰 내용을 바탕으로 자서전을 작성해주세요:\n\n{organized_content}"
        
        model = self.client.models.get(settings.gemini_model)
        response = await model.generate_content_async([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
        
        return response.text
    
    def _organize_conversations(self, conversations: list) -> str:
        """대화를 세션별로 정리"""
        organized = {}
        for conv in conversations:
            session_num = conv.get("session_number", 0)
            if session_num not in organized:
                organized[session_num] = []
            organized[session_num].append({
                "user": conv.get("user_message", ""),
                "ai": conv.get("ai_response", "")
            })
        
        result = ""
        for session_num in sorted(organized.keys()):
            session_template = SESSION_TEMPLATES[session_num]
            result += f"\n\n## {session_template['title']}\n"
            for conv in organized[session_num]:
                result += f"\n사용자: {conv['user']}\n"
                result += f"AI: {conv['ai']}\n"
        
        return result

gemini_service = GeminiService()