from typing import Dict, List, Optional, Any
from ..models.session_templates import SESSION_TEMPLATES, MEMORY_GUIDE_SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)

class ConversationManager:
    """대화 흐름을 관리하는 클래스"""
    
    def __init__(self):
        self.session_states: Dict[str, Dict[str, Any]] = {}
    
    def initialize_session(self, session_id: int, session_number: int) -> Dict[str, Any]:
        """세션 초기화"""
        session_key = f"session_{session_id}"
        session_template = SESSION_TEMPLATES[session_number]
        
        self.session_states[session_key] = {
            "session_number": session_number,
            "session_title": session_template["title"],
            "questions": session_template["questions"].copy(),
            "current_question_index": 0,
            "conversation_count": 0,
            "is_session_started": False,
            "last_user_response": None,
            "follow_up_count": 0
        }
        
        return self.session_states[session_key]
    
    def get_session_opening(self, session_id: int) -> str:
        """세션 시작 인사말 생성"""
        session_key = f"session_{session_id}"
        if session_key not in self.session_states:
            return "세션이 초기화되지 않았습니다."
        
        session_state = self.session_states[session_key]
        session_title = session_state["session_title"]
        
        opening = f"""안녕하세요, 어르신의 소중한 인생 이야기를 귀담아듣고 아름다운 자서전으로 기록해 드릴 '기억의 안내자'입니다. 제가 곁에서 길잡이가 되어드릴 테니, 그저 오랜 친구에게 이야기하듯 편안한 마음으로 함께해 주시면 됩니다. 

오늘은 '{session_title}'에 대해 이야기를 나눠보고자 합니다. 준비되셨을 때 편하게 말씀해주세요."""
        
        session_state["is_session_started"] = True
        return opening
    
    def get_next_question(self, session_id: int) -> Optional[str]:
        """다음 주요 질문 가져오기"""
        session_key = f"session_{session_id}"
        if session_key not in self.session_states:
            return None
        
        session_state = self.session_states[session_key]
        questions = session_state["questions"]
        current_index = session_state["current_question_index"]
        
        if current_index < len(questions):
            question = questions[current_index]
            session_state["current_question_index"] += 1
            session_state["follow_up_count"] = 0
            return question
        
        return None
    
    def should_ask_follow_up(self, session_id: int, user_response: str) -> bool:
        """꼬리 질문이 필요한지 판단"""
        session_key = f"session_{session_id}"
        if session_key not in self.session_states:
            return False
        
        session_state = self.session_states[session_key]
        
        # 간단한 답변이거나 꼬리 질문이 아직 2개 미만인 경우
        if (len(user_response.strip()) < 50 or 
            session_state["follow_up_count"] < 2):
            return True
        
        return False
    
    def generate_follow_up_question(self, session_id: int, user_response: str) -> Optional[str]:
        """사용자 답변에 기반한 꼬리 질문 생성"""
        session_key = f"session_{session_id}"
        if session_key not in self.session_states:
            return None
        
        session_state = self.session_states[session_key]
        session_state["follow_up_count"] += 1
        session_state["last_user_response"] = user_response
        
        # 꼬리 질문 템플릿들
        follow_up_templates = [
            "그때 어떤 감정이 드셨나요?",
            "그 경험이 어르신에게 어떤 영향을 미쳤나요?",
            "그 순간을 더 자세히 들려주실 수 있나요?",
            "그때 주변 사람들의 반응은 어떠했나요?",
            "그 일이 있은 후 어떤 변화가 있었나요?",
            "지금 생각해보시면 그때 어떤 마음이셨을까요?",
            "그런 경험을 통해 무엇을 배우셨나요?"
        ]
        
        # 단순하게 순환하며 선택 (추후 AI로 개선 가능)
        template_index = session_state["follow_up_count"] % len(follow_up_templates)
        return follow_up_templates[template_index]
    
    def can_move_to_next_question(self, session_id: int) -> bool:
        """다음 질문으로 넘어갈 수 있는지 판단"""
        session_key = f"session_{session_id}"
        if session_key not in self.session_states:
            return False
        
        session_state = self.session_states[session_key]
        
        # 최소 1번의 답변과 1번의 꼬리 질문이 있었다면 다음으로 넘어가기 가능
        return session_state["follow_up_count"] >= 1
    
    def get_session_closure(self, session_id: int, next_session_title: Optional[str] = None) -> str:
        """세션 마무리 멘트"""
        session_key = f"session_{session_id}"
        if session_key not in self.session_states:
            return "감사합니다."
        
        session_state = self.session_states[session_key]
        session_title = session_state["session_title"]
        
        closure = f"오늘 '{session_title}'에 대한 어르신의 소중한 경험 덕분에 더 깊이 이해하게 되었습니다."
        
        if next_session_title:
            closure += f" 다음에는 '{next_session_title}'에 대한 이야기를 나눠보면 좋겠습니다."
        
        closure += " 오늘도 소중한 이야기 들려주셔서 정말 감사합니다."
        
        return closure
    
    def get_session_progress(self, session_id: int) -> Dict[str, Any]:
        """세션 진행 상황 반환"""
        session_key = f"session_{session_id}"
        if session_key not in self.session_states:
            return {}
        
        session_state = self.session_states[session_key]
        total_questions = len(session_state["questions"])
        current_index = session_state["current_question_index"]
        
        return {
            "session_title": session_state["session_title"],
            "total_questions": total_questions,
            "current_question": current_index,
            "progress_percent": (current_index / total_questions) * 100,
            "conversation_count": session_state["conversation_count"],
            "is_completed": current_index >= total_questions
        }
    
    def update_conversation_count(self, session_id: int):
        """대화 수 증가"""
        session_key = f"session_{session_id}"
        if session_key in self.session_states:
            self.session_states[session_key]["conversation_count"] += 1
    
    def is_session_completed(self, session_id: int) -> bool:
        """세션이 완료되었는지 확인"""
        session_key = f"session_{session_id}"
        if session_key not in self.session_states:
            return False
        
        session_state = self.session_states[session_key]
        return session_state["current_question_index"] >= len(session_state["questions"])

# 글로벌 인스턴스
conversation_manager = ConversationManager()