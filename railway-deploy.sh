#!/bin/bash

# Railway 배포용 스크립트

echo "🚀 He'story Backend 배포 시작..."

# 백엔드 디렉토리로 이동
cd backend

# 의존성 설치
echo "📦 의존성 설치 중..."
pip install -r requirements.txt

# 환경 변수 확인
echo "🔍 환경 변수 확인..."
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY가 설정되지 않았습니다."
fi

if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL이 설정되지 않았습니다."
fi

# 서버 실행
echo "🎯 서버 실행..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}