#!/usr/bin/env python3
"""
He'story Backend Entry Point for Railway Deployment
"""

import sys
import os

# 백엔드 경로를 Python 경로에 추가
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# 백엔드 앱 import
from backend.app.main import app

# Railway에서 사용할 앱 객체
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