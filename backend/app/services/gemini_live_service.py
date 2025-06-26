import asyncio
import json
import base64
import logging
from typing import Optional, AsyncGenerator
import websockets
from google import genai
from ..config import settings
from ..models.session_templates import SESSION_TEMPLATES, MEMORY_GUIDE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class GeminiLiveService:
    """실제 Gemini Live API를 사용한 실시간 음성 대화 서비스"""
    
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.google_api_key,
            http_options={"api_version": "v1beta"}
        )
        self.active_sessions = {}
    
    async def start_live_session(self, session_id: int, session_number: int) -> str:
        """실시간 음성 세션 시작"""
        if settings.google_api_key.startswith("AIzaSyDummy"):
            raise Exception("Real Google API key required for live audio")
        
        try:
            session_template = SESSION_TEMPLATES[session_number]
            
            # Gemini Live API 설정
            config = {
                "generation_config": {
                    "response_modalities": ["AUDIO"],
                    "speech_config": {
                        "voice_config": {
                            "prebuilt_voice_config": {
                                "voice_name": "Pico"  # 한국어 지원 음성
                            }
                        }
                    }
                },
                "system_instruction": {
                    "parts": [{
                        "text": f"""{MEMORY_GUIDE_SYSTEM_PROMPT}

현재 세션: {session_template['title']}
세션 목표: {session_template.get('description', '')}

당신은 지금 실시간 음성 대화를 통해 이 분의 소중한 인생 이야기를 듣고 있습니다. 
자연스럽고 따뜻한 목소리로 대화해주세요. 
사용자가 말을 멈추면 적절한 타이밍에 질문이나 공감을 표현해주세요."""
                    }]
                }
            }
            
            # Live API 세션 생성
            model = self.client.models.get(settings.gemini_live_model)
            live_session = model.start_chat(**config)
            
            session_key = f"live_{session_id}_{session_number}"
            self.active_sessions[session_key] = {
                "session": live_session,
                "session_id": session_id,
                "session_number": session_number,
                "websocket": None
            }
            
            logger.info(f"Started live session: {session_key}")
            return session_key
            
        except Exception as e:
            logger.error(f"Failed to start live session: {e}")
            raise
    
    async def handle_websocket_connection(self, websocket, session_key: str):
        """WebSocket 연결 처리 및 실시간 오디오 스트리밍"""
        if session_key not in self.active_sessions:
            await websocket.close(code=4004, reason="Session not found")
            return
        
        session_info = self.active_sessions[session_key]
        session_info["websocket"] = websocket
        live_session = session_info["session"]
        
        try:
            # 세션 시작 인사
            session_template = SESSION_TEMPLATES[session_info["session_number"]]
            opening_message = f"""안녕하세요! 오늘은 "{session_template['title']}"에 대한 이야기를 들려주세요. 
편안하게 시작해보겠습니다. 어떤 기억부터 시작하고 싶으신가요?"""
            
            # AI 음성으로 인사 생성
            opening_audio = await self._generate_speech(opening_message)
            if opening_audio:
                await websocket.send(json.dumps({
                    "type": "audio_response",
                    "audio_data": opening_audio,
                    "text": opening_message
                }))
            
            # 실시간 오디오 처리 루프
            async def process_incoming_audio():
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        
                        if data["type"] == "audio_chunk":
                            # 실시간 오디오 청크를 Gemini Live API로 전송
                            audio_data = base64.b64decode(data["audio_data"])
                            await live_session.send(audio_data)
                        
                        elif data["type"] == "audio_end":
                            # 사용자 발화 종료 - AI 응답 요청
                            response = await live_session.receive()
                            
                            if response.audio:
                                # AI 음성 응답을 클라이언트로 전송
                                audio_b64 = base64.b64encode(response.audio).decode()
                                await websocket.send(json.dumps({
                                    "type": "audio_response", 
                                    "audio_data": audio_b64,
                                    "text": response.text or ""
                                }))
                        
                        elif data["type"] == "text_message":
                            # 텍스트 메시지 처리
                            text_response = await live_session.send_text(data["message"])
                            speech_audio = await self._generate_speech(text_response.text)
                            
                            await websocket.send(json.dumps({
                                "type": "audio_response",
                                "audio_data": speech_audio,
                                "text": text_response.text
                            }))
                            
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "메시지 처리 중 오류가 발생했습니다."
                        }))
            
            # 실시간 오디오 처리 시작
            await process_incoming_audio()
            
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed for session {session_key}")
        except Exception as e:
            logger.error(f"Error in live session {session_key}: {e}")
        finally:
            # 세션 정리
            await self.end_live_session(session_key)
    
    async def _generate_speech(self, text: str) -> Optional[str]:
        """텍스트를 음성으로 변환"""
        try:
            # Google TTS 또는 Gemini의 음성 생성 기능 사용
            speech_response = await self.client.agenerate_content(
                model=settings.gemini_live_model,
                contents=[{"text": text}],
                config={
                    "response_modalities": ["AUDIO"],
                    "speech_config": {
                        "voice_config": {
                            "prebuilt_voice_config": {
                                "voice_name": "Pico"
                            }
                        }
                    }
                }
            )
            
            if speech_response.audio:
                return base64.b64encode(speech_response.audio).decode()
            return None
            
        except Exception as e:
            logger.error(f"Speech generation error: {e}")
            return None
    
    async def end_live_session(self, session_key: str):
        """실시간 세션 종료"""
        if session_key in self.active_sessions:
            session_info = self.active_sessions[session_key]
            
            try:
                if session_info["session"]:
                    await session_info["session"].close()
            except Exception as e:
                logger.error(f"Error closing live session: {e}")
            
            del self.active_sessions[session_key]
            logger.info(f"Ended live session: {session_key}")

# 전역 인스턴스
gemini_live_service = GeminiLiveService()