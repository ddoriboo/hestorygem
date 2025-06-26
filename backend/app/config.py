from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    app_name: str = "He'story"
    version: str = "1.0.0"
    debug: bool = True
    
    # Database
    database_url: str = "postgresql://user:password@localhost/hestory"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google API
    google_api_key: str
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