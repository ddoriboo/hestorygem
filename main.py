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
    print("Attempting to import backend app...")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir('.')}")
    if os.path.exists('backend'):
        print(f"Backend directory contents: {os.listdir('backend')}")
        if os.path.exists('backend/app'):
            print(f"Backend/app directory contents: {os.listdir('backend/app')}")
    
    from backend.app.main import app
    print("Successfully imported backend app!")
    
    # Railway에서 사용할 앱 객체
    application = app
    
except Exception as e:
    print(f"Error importing backend: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exc()
    print("Falling back to basic FastAPI app")
    
    # 기본 FastAPI 앱 생성 (fallback)
    from fastapi import FastAPI
    application = FastAPI(title="He'story API", description="Railway Deployment")
    
    @application.get("/")
    async def root():
        return {"message": "He'story API is running on Railway", "status": "ok", "note": "Backend import failed - check /debug for details"}
    
    @application.get("/health")
    async def health():
        return {"status": "healthy", "deployment": "railway"}
    
    @application.get("/debug")
    async def debug():
        import sys
        debug_info = {
            "message": "Backend imported successfully! This debug endpoint should not be visible.",
            "working_directory": os.getcwd(),
            "directory_contents": os.listdir('.') if os.path.exists('.') else [],
            "backend_exists": os.path.exists('backend'),
            "python_path": sys.path,
            "environment_vars": {k: v for k, v in os.environ.items() if 'SECRET' not in k and 'KEY' not in k},
        }
        if os.path.exists('backend'):
            debug_info["backend_contents"] = os.listdir('backend')
            if os.path.exists('backend/app'):
                debug_info["backend_app_contents"] = os.listdir('backend/app')
        return debug_info

# uvicorn이 직접 참조할 수 있도록 app도 설정
app = application

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )