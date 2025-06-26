from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    app_name: str = "He'story"
    version: str = "1.0.0"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./hestory.db"  # SQLite 기본값 (Railway에서 PostgreSQL 설정 시 덮어씀)
    
    # Security
    secret_key: str = "railway-default-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google API
    google_api_key: str = "demo-key"  # Railway에서 실제 키 설정 필요
    gemini_model: str = "models/gemini-2.0-flash-exp"
    gemini_live_model: str = "models/gemini-2.0-flash-live-001"
    
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

settings = Settings()