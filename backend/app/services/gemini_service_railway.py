import asyncio
import base64
import io
import os
from typing import Optional, AsyncGenerator

# PyAudio는 Railway에서 선택적으로 import
try:
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    
import google.generativeai as genai
from ..config import settings
from ..models.session_templates import SESSION_TEMPLATES, MEMORY_GUIDE_SYSTEM_PROMPT
from .conversation_manager import conversation_manager

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        # PyAudio는 사용 가능한 경우에만 초기화
        if AUDIO_AVAILABLE:
            self.pya = pyaudio.PyAudio()
        else:
            self.pya = None
        
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """일반적인 텍스트 생성"""
        # API 키가 없거나 더미값인 경우 fallback 응답
        if not settings.google_api_key or settings.google_api_key.startswith("AIzaSyDummy"):
            print(f"Using fallback response - API key: {settings.google_api_key[:10]}...")
            return self._get_fallback_response(prompt)
        
        try:
            model = genai.GenerativeModel(settings.gemini_model)
            
            # 시스템 프롬프트와 사용자 메시지 결합
            full_prompt = f"{system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
            
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, user_message: str) -> str:
        """API 키가 없을 때 사용할 fallback 응답들"""
        fallback_responses = [
            "정말 소중한 이야기네요. 그때의 감정이 어떠셨는지 좀 더 자세히 들려주실 수 있을까요?",
            "아, 그런 경험이 있으셨군요. 그 일이 당시 삶에 어떤 영향을 미쳤는지 궁금합니다.",
            "말씀해주셔서 감사합니다. 그 순간이 특별했던 이유가 무엇인지 더 이야기해주세요.",
            "정말 인상 깊은 이야기입니다. 그 경험을 통해 배우신 것이 있다면 무엇인가요?",
            "그렇게 힘든 시간을 보내셨군요. 어떻게 그 어려움을 극복하셨는지 들려주세요.",
            "아름다운 추억이네요. 그때의 행복했던 순간들을 좀 더 구체적으로 이야기해주실래요?",
            "참 의미 있는 시간이었을 것 같습니다. 그 경험이 지금의 당신에게 어떤 의미인지 말씀해주세요."
        ]
        
        # 사용자 메시지 길이에 따라 다른 응답
        if len(user_message) < 10:
            return "조금 더 자세히 이야기해주시면 좋겠어요. 어떤 기분이셨는지, 무슨 일이 있었는지 편하게 말씀해주세요."
        
        import random
        return random.choice(fallback_responses)
    
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
        try:
            return await self.generate_contextual_response(
                session_number, user_message, conversation_history
            )
        except Exception as e:
            print(f"Contextual response error: {e}")
            return self._get_fallback_response(user_message)
    
    async def generate_contextual_response(
        self,
        session_number: int,
        user_message: str,
        conversation_history: list = []
    ) -> str:
        """맥락적 응답 생성 (백업 메서드)"""
        # API 키가 없거나 더미값인 경우 fallback
        if not settings.google_api_key or settings.google_api_key.startswith("AIzaSyDummy"):
            print(f"Using fallback contextual response - API key: {settings.google_api_key[:10] if settings.google_api_key else 'None'}...")
            return self._get_session_specific_response(session_number, user_message)
        
        try:
            session_template = SESSION_TEMPLATES[session_number]
            
            system_prompt = f"""{MEMORY_GUIDE_SYSTEM_PROMPT}

현재 세션: {session_template['title']}
세션 목표: {session_template.get('objective', session_template.get('description', ''))}

현재 사용자가 말씀하신 내용에 대해 '기억의 안내자'로서 적절한 응답을 해주세요."""
            
            # 대화 히스토리와 현재 메시지 결합
            full_context = system_prompt + "\n\n"
            
            # 최근 대화 히스토리 추가
            for conv in conversation_history[-3:]:
                if conv.get("user_message"):
                    full_context += f"사용자: {conv.get('user_message', '')}\n"
                if conv.get("ai_response"):
                    full_context += f"기억의 안내자: {conv.get('ai_response', '')}\n"
            
            full_context += f"사용자: {user_message}\n기억의 안내자:"
            
            model = genai.GenerativeModel(settings.gemini_model)
            response = model.generate_content(full_context)
            return response.text
        except Exception as e:
            print(f"Generate contextual response error: {e}")
            return self._get_session_specific_response(session_number, user_message)
    
    def _get_session_specific_response(self, session_number: int, user_message: str) -> str:
        """세션별 맞춤 fallback 응답"""
        session_responses = {
            0: [  # 프롤로그 - 나의 뿌리와 세상의 시작
                "어린 시절 살았던 동네는 어떤 모습이었나요?",
                "가족 중에서 가장 기억에 남는 분은 누구신가요?",
                "어렸을 때 가장 좋아했던 놀이는 무엇이었나요?"
            ],
            1: [  # 어린 시절의 보물같은 기억들
                "초등학교 때 가장 기억에 남는 선생님은 어떤 분이셨나요?",
                "어린 시절 가장 친했던 친구와의 추억을 들려주세요.",
                "그 시절 가장 설렜던 순간은 언제였나요?"
            ],
            2: [  # 꿈을 키우던 청소년기
                "중고등학교 시절 꿈꿨던 미래는 어떤 모습이었나요?",
                "청소년기에 가장 힘들었던 일은 무엇이었나요?",
                "그 시절 가장 열정적으로 했던 활동이 있나요?"
            ]
        }
        
        if session_number in session_responses:
            import random
            return random.choice(session_responses[session_number])
        else:
            return self._get_fallback_response(user_message)
    
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
        
        model = genai.GenerativeModel(settings.gemini_model)
        
        # 간단한 프롬프트로 자서전 생성
        full_prompt = f"{system_prompt}\n\n{prompt}"
        response = model.generate_content(full_prompt)
        
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