import asyncio
import base64
import io
from typing import Optional, Dict, Any
import pyaudio
from google import genai
from ..config import settings
from ..models.session_templates import SESSION_TEMPLATES, MEMORY_GUIDE_SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)

class LiveInterviewService:
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.google_api_key,
            http_options={"api_version": "v1beta"}
        )
        self.pya = pyaudio.PyAudio()
        self.active_sessions: Dict[str, Any] = {}
        
    async def start_live_interview(
        self, 
        user_id: int,
        session_id: int,
        session_number: int
    ) -> str:
        """실시간 음성 인터뷰 시작"""
        session_key = f"{user_id}_{session_id}"
        
        if session_key in self.active_sessions:
            return session_key
        
        session_template = SESSION_TEMPLATES[session_number]
        
        # Gemini Live API 설정
        config = {
            "response_modalities": ["AUDIO"],
            "system_instruction": f"""{MEMORY_GUIDE_SYSTEM_PROMPT}

현재 세션: {session_template['title']}
세션 목표: {session_template['objective']}
세션 질문들: {', '.join(session_template['questions'][:3])}...

실시간 음성 대화이므로 다음 사항을 추가로 준수하세요:
- 음성으로 대화하므로 자연스럽고 말하기 쉬운 표현을 사용하세요
- 너무 긴 문장보다는 적당한 길이로 나누어 말하세요
- 상대방의 말이 끝나길 기다리고 적절한 타이밍에 응답하세요
- 감정을 목소리로 표현할 수 있으므로 따뜻하고 공감적인 톤을 유지하세요"""
        }
        
        try:
            # Live API 연결
            session = await self.client.aio.live.connect(
                model=settings.gemini_live_model,
                config=config
            )
            
            self.active_sessions[session_key] = {
                "session": session,
                "user_id": user_id,
                "session_id": session_id,
                "audio_queue": asyncio.Queue(),
                "transcript_queue": asyncio.Queue(),
                "is_active": True
            }
            
            # 백그라운드 태스크 시작
            asyncio.create_task(self._handle_live_session(session_key))
            
            # 초기 인사 메시지 전송
            await session.send(
                text=f"안녕하세요! 오늘은 '{session_template['title']}'에 대해 이야기를 나눠보려고 합니다. 편안하게 이야기해주세요.",
                end_of_turn=True
            )
            
            return session_key
            
        except Exception as e:
            logger.error(f"Failed to start live interview: {e}")
            raise
    
    async def send_audio_chunk(self, session_key: str, audio_data: bytes):
        """오디오 청크 전송"""
        if session_key not in self.active_sessions:
            raise ValueError("Session not found")
        
        session_info = self.active_sessions[session_key]
        session = session_info["session"]
        
        # PCM 오디오 데이터를 Live API로 전송
        await session.send(
            audio={
                "data": audio_data,
                "mime_type": "audio/pcm",
                "sample_rate": settings.send_sample_rate,
                "channels": settings.audio_channels
            }
        )
    
    async def get_audio_response(self, session_key: str) -> Optional[bytes]:
        """AI 응답 오디오 가져오기"""
        if session_key not in self.active_sessions:
            return None
        
        session_info = self.active_sessions[session_key]
        audio_queue = session_info["audio_queue"]
        
        try:
            audio_data = await asyncio.wait_for(audio_queue.get(), timeout=0.1)
            return audio_data
        except asyncio.TimeoutError:
            return None
    
    async def get_transcript(self, session_key: str) -> Optional[Dict[str, str]]:
        """대화 텍스트 가져오기"""
        if session_key not in self.active_sessions:
            return None
        
        session_info = self.active_sessions[session_key]
        transcript_queue = session_info["transcript_queue"]
        
        try:
            transcript = await asyncio.wait_for(transcript_queue.get(), timeout=0.1)
            return transcript
        except asyncio.TimeoutError:
            return None
    
    async def end_live_interview(self, session_key: str) -> Dict[str, Any]:
        """실시간 인터뷰 종료"""
        if session_key not in self.active_sessions:
            raise ValueError("Session not found")
        
        session_info = self.active_sessions[session_key]
        session_info["is_active"] = False
        
        # 세션 종료
        session = session_info["session"]
        await session.close()
        
        # 전체 대화 내용 반환
        transcripts = []
        while not session_info["transcript_queue"].empty():
            transcripts.append(await session_info["transcript_queue"].get())
        
        del self.active_sessions[session_key]
        
        return {
            "session_id": session_info["session_id"],
            "transcripts": transcripts
        }
    
    async def _handle_live_session(self, session_key: str):
        """Live 세션 처리 (백그라운드 태스크)"""
        session_info = self.active_sessions[session_key]
        session = session_info["session"]
        
        try:
            while session_info["is_active"]:
                # AI 응답 수신
                async for response in session.receive():
                    if response.audio:
                        # 오디오 데이터를 큐에 추가
                        await session_info["audio_queue"].put(response.audio.data)
                    
                    if response.text:
                        # 텍스트 응답을 트랜스크립트 큐에 추가
                        await session_info["transcript_queue"].put({
                            "role": "assistant",
                            "content": response.text
                        })
                    
                    if response.tool_calls:
                        # 도구 호출 처리 (필요한 경우)
                        pass
                        
        except Exception as e:
            logger.error(f"Error in live session handler: {e}")
        finally:
            session_info["is_active"] = False

live_interview_service = LiveInterviewService()