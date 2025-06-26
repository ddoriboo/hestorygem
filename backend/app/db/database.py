from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import settings
import os

# SQLite URL에 대한 특별 처리 (Railway 환경)
database_url = settings.database_url
if database_url.startswith("sqlite:///"):
    # SQLite 파일이 저장될 디렉토리 생성
    db_dir = os.path.dirname(database_url.replace("sqlite:///", ""))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    # SQLite 엔진에 특별 옵션 추가
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False}  # SQLite threading 이슈 해결
    )
else:
    engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()