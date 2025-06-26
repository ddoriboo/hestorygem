# He'story Backend API

AI 기반 시니어 자서전 작성 서비스의 백엔드 API 서버입니다.

## 주요 기능

### 🎯 핵심 시스템
- **기억의 안내자**: 전문적인 AI 인터뷰어 시스템
- **12개 구조화된 세션**: 인생 전반을 다루는 체계적인 인터뷰 진행
- **실시간 음성 인터뷰**: Gemini Live API를 통한 자연스러운 대화
- **텍스트 인터뷰**: 웹 기반 채팅 인터페이스 지원
- **자동 자서전 생성**: 대화 내용 기반 완성된 자서전 제작

### 🔧 기술 스택
- **Framework**: FastAPI 0.109.0
- **AI**: Google Gemini API (Live API, Text Generation)
- **Database**: PostgreSQL + SQLAlchemy
- **Authentication**: JWT + OAuth2
- **Real-time**: WebSocket
- **Audio**: PyAudio

## 설치 및 실행

### 1. 환경 설정
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp ../.env.example ../.env
# .env 파일에서 GOOGLE_API_KEY 설정
```

### 2. 데이터베이스 설정
```bash
# PostgreSQL 실행 (Docker)
docker run --name hestory-db -e POSTGRES_PASSWORD=hestory123 -e POSTGRES_DB=hestory -e POSTGRES_USER=hestory -p 5432:5432 -d postgres:15-alpine

# 또는 기존 PostgreSQL 사용 시 .env에서 DATABASE_URL 수정
```

### 3. 서버 실행
```bash
# 개발 모드 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 Docker Compose 사용
cd ..
docker-compose up
```

### 4. API 문서 확인
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 🔐 인증 (Auth)
```
POST /api/auth/register    # 회원가입 (12개 세션 자동 생성)
POST /api/auth/token       # 로그인
GET  /api/auth/me          # 사용자 정보 조회
```

### 📚 세션 관리 (Sessions)
```
GET  /api/sessions/                           # 사용자 세션 목록
GET  /api/sessions/{session_id}               # 특정 세션 조회
PATCH /api/sessions/{session_id}              # 세션 상태 업데이트
GET  /api/sessions/{session_id}/progress      # 세션 진행률
GET  /api/sessions/{session_id}/flow-status   # 대화 흐름 상태
POST /api/sessions/{session_id}/initialize-flow # 세션 흐름 초기화
```

### 💬 대화 관리 (Conversations)
```
GET  /api/conversations/session/{session_id}  # 세션별 대화 조회
POST /api/conversations/interview             # 텍스트 인터뷰
WebSocket /api/conversations/live/{session_id} # 실시간 음성 인터뷰
POST /api/conversations/generate-autobiography # 자서전 생성
```

### 📖 자서전 (Autobiography)
```
POST /api/autobiography/generate              # 자서전 생성
GET  /api/autobiography/preview               # 미리보기
GET  /api/autobiography/status                # 생성 가능 상태 확인
```

## 12개 세션 구조

1. **프롤로그** - 나의 뿌리와 세상의 시작
2. **제1장** - 기억의 첫 페이지, 유년 시절
3. **제2장** - 꿈과 방황의 시간, 학창 시절
4. **제3장** - 세상으로 내디딘 첫걸음, 청년 시절
5. **제4장** - 인생의 동반자를 만나다, 사랑과 결혼
6. **제5장** - '아버지'라는 이름의 무게, 자녀의 탄생과 양육
7. **제6장** - 치열했던 삶의 현장, 사회생활과 직업
8. **제7장** - 인생의 나이테, 중년의 나날들
9. **제8장** - 삶을 관통하는 지혜, 나의 신념과 철학
10. **제9장** - 돌아보고, 감사하고, 용서하며
11. **제10장** - 사랑하는 이들에게 남기는 말
12. **에필로그** - 내 삶이라는 책을 덮으며

## 사용 예시

### 1. 회원가입 및 로그인
```python
import httpx

# 회원가입
response = httpx.post("http://localhost:8000/api/auth/register", json={
    "email": "user@example.com",
    "username": "user123",
    "password": "password123",
    "full_name": "홍길동",
    "birth_year": 1950
})

# 로그인
response = httpx.post("http://localhost:8000/api/auth/token", data={
    "username": "user123",
    "password": "password123"
})
token = response.json()["access_token"]
```

### 2. 텍스트 인터뷰 진행
```python
headers = {"Authorization": f"Bearer {token}"}

# 첫 번째 세션으로 인터뷰 시작
response = httpx.post("http://localhost:8000/api/conversations/interview", 
    headers=headers,
    json={
        "session_id": 1,
        "conversation_type": "text",
        "message": "안녕하세요, 인터뷰를 시작하겠습니다."
    }
)

ai_response = response.json()["ai_response"]
print(f"AI: {ai_response}")
```

### 3. 세션 진행 상황 확인
```python
response = httpx.get("http://localhost:8000/api/sessions/1/flow-status", 
    headers=headers)
    
status = response.json()
print(f"진행률: {status['flow_progress_percent']}%")
print(f"다음 질문: {status['next_question']}")
```

## 시스템 테스트

백엔드 시스템을 테스트하려면 다음 스크립트를 실행하세요:

```bash
# 세션 템플릿 확인
python test_interview.py templates

# 대화 관리자 테스트
python test_interview.py manager

# 전체 인터뷰 플로우 테스트 (Gemini API 키 필요)
python test_interview.py full
```

## 환경 변수

```bash
# 필수
GOOGLE_API_KEY=your_google_api_key_here
DATABASE_URL=postgresql://user:password@localhost/hestory
SECRET_KEY=your_jwt_secret_key

# 선택사항
ENVIRONMENT=development
GEMINI_MODEL=models/gemini-2.0-flash-exp
GEMINI_LIVE_MODEL=models/gemini-2.0-flash-live-001
```

## 개발 가이드

### 새로운 세션 추가
1. `models/session_templates.py`에서 `SESSION_TEMPLATES` 수정
2. 데이터베이스 마이그레이션 실행
3. 테스트 케이스 추가

### AI 프롬프트 수정
- 시스템 프롬프트: `models/session_templates.py`의 `MEMORY_GUIDE_SYSTEM_PROMPT`
- 세션별 프롬프트: 각 세션의 `questions` 배열

### 새로운 API 엔드포인트 추가
1. `api/` 폴더에 새 라우터 파일 생성
2. `main.py`에서 라우터 등록
3. 스키마와 모델 정의

## 배포

### Docker 배포
```bash
docker build -t hestory-backend .
docker run -p 8000:8000 --env-file .env hestory-backend
```

### 프로덕션 배포
```bash
# Gunicorn 사용
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 문제 해결

### 일반적인 문제
1. **Gemini API 오류**: `GOOGLE_API_KEY` 확인
2. **데이터베이스 연결 오류**: PostgreSQL 서비스 및 연결 정보 확인
3. **오디오 관련 오류**: PyAudio 시스템 의존성 설치

### 로그 확인
```bash
# 애플리케이션 로그
tail -f logs/app.log

# Docker 로그
docker-compose logs -f backend
```

## 라이선스

MIT License - 자세한 내용은 LICENSE 파일을 참조하세요.