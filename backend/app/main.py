from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
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

# 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(autobiography.router, prefix="/api/autobiography", tags=["autobiography"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to He'story API",
        "version": settings.version,
        "description": "AI 기반 시니어 자서전 작성 서비스"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )