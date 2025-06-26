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

# 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(autobiography.router, prefix="/api/autobiography", tags=["autobiography"])

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

# 프론트엔드 라우팅을 위한 catch-all
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # API 경로가 아닌 경우 프론트엔드 index.html 반환
    if not full_path.startswith("api/"):
        static_dir = "/app/static"
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    
    # 404 for other paths
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