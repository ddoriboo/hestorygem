from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from contextlib import asynccontextmanager
import logging
from .config import settings
from .api import auth, sessions, conversations, autobiography
from .db.database import engine
from .models import user, session, conversation

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 데이터베이스 테이블 생성 (에러 처리 추가)
try:
    logger.info("Creating database tables...")
    user.Base.metadata.create_all(bind=engine)
    session.Base.metadata.create_all(bind=engine)
    conversation.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to create database tables: {e}")
    # Railway 환경에서는 계속 진행 (나중에 테이블 생성 재시도 가능)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시
    logger.info("Starting He'story application...")
    yield
    # 종료 시
    logger.info("Shutting down He'story application...")

# FastAPI 앱 생성
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (프론트엔드)
static_dir = "/app/static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 라우터 등록 (API 우선순위 보장)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(autobiography.router, prefix="/api/autobiography", tags=["autobiography"])

# API 디버깅을 위한 엔드포인트
@app.get("/api/debug")
async def api_debug():
    return {
        "message": "API is working",
        "available_endpoints": [
            "/api/auth/login",
            "/api/auth/register", 
            "/api/sessions",
            "/api/conversations",
            "/api/autobiography"
        ],
        "google_api_status": {
            "key_configured": bool(settings.google_api_key and not settings.google_api_key.startswith("AIzaSyDummy")),
            "key_prefix": settings.google_api_key[:10] if settings.google_api_key else None,
            "model": settings.gemini_model
        }
    }

@app.get("/")
async def root():
    # 프론트엔드 index.html 서빙
    static_dir = "/app/static"
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {
            "message": "Welcome to He'story API",
            "version": settings.version,
            "description": "AI 기반 시니어 자서전 작성 서비스",
            "note": "프론트엔드 빌드 파일을 찾을 수 없습니다."
        }

@app.get("/api")
async def api_root():
    return {
        "message": "Welcome to He'story API",
        "version": settings.version,
        "description": "AI 기반 시니어 자서전 작성 서비스"
    }

@app.get("/live")
async def live_interview_page():
    # 실시간 음성 인터뷰 페이지 서빙
    static_dir = "/app/static"
    live_path = os.path.join(static_dir, "live.html")
    if os.path.exists(live_path):
        return FileResponse(live_path)
    else:
        return {
            "message": "실시간 음성 인터뷰 기능",
            "note": "live.html 파일이 필요합니다",
            "fallback_url": "/"
        }

# 프론트엔드 라우팅을 위한 catch-all (API 경로 제외)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # API 경로는 무시 (다른 라우터에서 처리)
    if full_path.startswith("api"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # 정적 파일 확인
    static_dir = "/app/static"
    static_path = os.path.join(static_dir, full_path)
    if os.path.exists(static_path) and os.path.isfile(static_path):
        return FileResponse(static_path)
    
    # 그 외 모든 경우 index.html 반환 (SPA 라우팅)
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Not found")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "railway": "ok"}

@app.get("/healthz")
async def health_check_alt():
    return {"status": "healthy", "railway": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )