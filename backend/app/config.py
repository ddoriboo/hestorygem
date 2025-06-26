from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App
    app_name: str = "He'story"
    version: str = "1.0.0"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///app/hestory.db"  # SQLite 기본값 (Railway에서 PostgreSQL 설정 시 덮어씀)
    
    # Security
    secret_key: str = "hestory-railway-jwt-secret-key-2025"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24시간 (더 긴 세션)
    
    # Google API
    google_api_key: str  # Railway 환경변수에서 가져옴
    gemini_model: str = "gemini-pro"
    gemini_live_model: str = "gemini-pro"
    
    # Audio Settings
    audio_format: str = "pcm"
    audio_channels: int = 1
    send_sample_rate: int = 16000
    receive_sample_rate: int = 24000
    chunk_size: int = 1024
    
    # CORS
    backend_cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Google API 키 디버깅
        print(f"Google API Key loaded: {self.google_api_key[:10] if self.google_api_key else 'None'}...")
        print(f"Google API Key length: {len(self.google_api_key) if self.google_api_key else 0}")
        print(f"Environment GOOGLE_API_KEY: {os.environ.get('GOOGLE_API_KEY', 'Not set')[:10]}...")

settings = Settings()