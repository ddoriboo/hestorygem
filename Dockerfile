# Railway 배포용 Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치 (PostgreSQL 클라이언트 포함)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 백엔드 코드 복사
COPY backend/ ./backend/
COPY main.py .

# 간단한 정적 프론트엔드 생성 (React 빌드 대신)
WORKDIR /app
RUN mkdir -p ./static
COPY webapp.html ./static/index.html
COPY webapp_live.html ./static/live.html

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PORT=8000

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "main:application", "--host", "0.0.0.0", "--port", "8000"]