from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime
import os
if os.environ.get('RAILWAY_DEPLOYMENT'):
    from .gemini_service_railway import gemini_service
else:
    from .gemini_service import gemini_service
from ..models.session_templates import SESSION_TEMPLATES
import logging

logger = logging.getLogger(__name__)

class AutobiographyService:
    def __init__(self):
        self.gemini = gemini_service
    
    async def generate_autobiography(
        self, 
        user_data: Dict[str, Any],
        conversations: List[Dict[str, Any]]
    ) -> str:
        """대화 내용을 바탕으로 자서전 생성"""
        
        # 대화를 세션별로 정리
        organized_conversations = self._organize_by_session(conversations)
        
        # 자서전 생성을 위한 프롬프트 구성
        system_prompt = f"""당신은 전문적인 자서전 작가입니다.
주어진 인터뷰 내용을 바탕으로 감동적이고 잘 구성된 자서전을 작성해주세요.

저자 정보:
- 이름: {user_data.get('full_name', '익명')}
- 출생년도: {user_data.get('birth_year', '알 수 없음')}

작성 지침:
1. 1인칭 시점으로 작성하세요 (나는, 내가 등)
2. 시간 순서대로 구성하되, 자연스러운 흐름을 유지하세요
3. 구체적인 에피소드와 감정을 생생하게 표현하세요
4. 각 장의 제목은 주어진 세션 제목을 그대로 사용하세요
5. 문학적이면서도 진솔한 문체를 사용하세요
6. 독자가 저자의 삶을 깊이 이해하고 공감할 수 있도록 작성하세요
7. 각 장은 2-4페이지 분량으로 작성하세요

형식:
- 제목: {user_data.get('full_name', '나')}의 이야기
- 각 장은 마크다운 형식의 ## 제목으로 시작
- 문단은 적절히 나누어 가독성을 높이세요"""
        
        # 대화 내용을 프롬프트로 변환
        conversation_prompt = self._create_conversation_prompt(organized_conversations)
        
        # Gemini API를 통해 자서전 생성
        autobiography = await self.gemini.generate_text(
            prompt=conversation_prompt,
            system_prompt=system_prompt
        )
        
        # 후처리: 형식 정리 및 검증
        autobiography = self._post_process_autobiography(autobiography, user_data)
        
        return autobiography
    
    def _organize_by_session(self, conversations: List[Dict[str, Any]]) -> Dict[int, List[Dict]]:
        """대화를 세션별로 정리"""
        organized = {}
        
        for conv in conversations:
            session_num = conv.get('session_number', 0)
            if session_num not in organized:
                organized[session_num] = {
                    'title': conv.get('session_title', ''),
                    'conversations': []
                }
            
            organized[session_num]['conversations'].append({
                'user': conv.get('user_message', ''),
                'ai': conv.get('ai_response', ''),
                'type': conv.get('conversation_type', 'text'),
                'created_at': conv.get('created_at')
            })
        
        return organized
    
    def _create_conversation_prompt(self, organized_conversations: Dict) -> str:
        """대화 내용을 자서전 작성용 프롬프트로 변환"""
        prompt = "다음은 인터뷰 내용입니다. 이를 바탕으로 자서전을 작성해주세요:\n\n"
        
        for session_num in sorted(organized_conversations.keys()):
            session_data = organized_conversations[session_num]
            session_template = SESSION_TEMPLATES[session_num]
            
            prompt += f"\n## {session_template['title']}\n"
            prompt += f"세션 설명: {session_template['description']}\n\n"
            
            prompt += "대화 내용:\n"
            for conv in session_data['conversations']:
                # 사용자 발언만 주로 포함 (AI 질문은 맥락 파악용)
                if conv['user']:
                    prompt += f"- 나의 이야기: {conv['user']}\n"
                    if len(conv['user']) < 50:  # 짧은 답변인 경우 AI 질문도 포함
                        prompt += f"  (질문: {conv['ai'][:100]}...)\n"
            
            prompt += "\n"
        
        prompt += "\n위 인터뷰 내용을 바탕으로 자연스럽고 감동적인 자서전을 작성해주세요."
        
        return prompt
    
    def _post_process_autobiography(self, autobiography: str, user_data: Dict[str, Any]) -> str:
        """생성된 자서전 후처리"""
        # 제목 추가
        title = f"# {user_data.get('full_name', '나')}의 이야기\n\n"
        
        # 생성 날짜 추가
        date_str = datetime.now().strftime("%Y년 %m월 %d일")
        header = f"{title}*작성일: {date_str}*\n\n---\n\n"
        
        # 목차 생성
        toc = "## 목차\n\n"
        for template in SESSION_TEMPLATES:
            toc += f"- {template['title']}\n"
        toc += "\n---\n\n"
        
        # 최종 자서전 구성
        final_autobiography = header + toc + autobiography
        
        # 후기 추가
        epilogue = f"\n\n---\n\n*이 자서전은 He'story AI 서비스를 통해 {user_data.get('full_name', '저자')}님의 구술을 바탕으로 작성되었습니다.*"
        
        return final_autobiography + epilogue
    
    async def generate_pdf(self, autobiography_text: str, user_name: Optional[str] = None) -> bytes:
        """자서전을 PDF로 변환 (추후 구현)"""
        # PDF 생성 로직 구현
        # 현재는 간단한 텍스트 반환
        logger.info("PDF generation requested - feature to be implemented")
        return autobiography_text.encode('utf-8')
    
    def validate_conversations(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """대화 내용이 자서전 생성에 충분한지 검증"""
        session_coverage = {}
        total_word_count = 0
        
        for conv in conversations:
            session_num = conv.get('session_number', 0)
            if session_num not in session_coverage:
                session_coverage[session_num] = {
                    'count': 0,
                    'word_count': 0
                }
            
            session_coverage[session_num]['count'] += 1
            session_coverage[session_num]['word_count'] += len(
                conv.get('user_message', '').split()
            )
            total_word_count += len(conv.get('user_message', '').split())
        
        # 각 세션별 충분도 계산
        session_adequacy = {}
        for session_num, data in session_coverage.items():
            adequacy = min(100, (data['count'] / 5) * 50 + (data['word_count'] / 500) * 50)
            session_adequacy[session_num] = {
                'adequacy': adequacy,
                'is_sufficient': adequacy >= 60
            }
        
        return {
            'total_sessions': len(session_coverage),
            'total_conversations': sum(s['count'] for s in session_coverage.values()),
            'total_word_count': total_word_count,
            'session_adequacy': session_adequacy,
            'is_ready': (
                len(session_coverage) >= 3 and
                total_word_count >= 3000 and
                sum(1 for s in session_adequacy.values() if s['is_sufficient']) >= 3
            )
        }

autobiography_service = AutobiographyService()