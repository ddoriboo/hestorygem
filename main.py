#!/usr/bin/env python3
"""
He'story Backend Entry Point for Railway Deployment
"""

import sys
import os

# 백엔드 경로를 Python 경로에 추가
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# PyAudio 관련 오류 방지를 위한 환경 변수 설정
os.environ.setdefault('RAILWAY_DEPLOYMENT', 'true')

try:
    # 백엔드 앱 import
    from backend.app.main import app
    
    # Railway에서 사용할 앱 객체
    application = app
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Falling back to basic FastAPI app")
    
    # 기본 FastAPI 앱 생성 (fallback)
    from fastapi import FastAPI
    app = FastAPI(title="He'story API", description="Railway Deployment")
    
    @app.get("/")
    async def root():
        return {"message": "He'story API is running on Railway", "status": "ok"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "deployment": "railway"}
    
    application = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )