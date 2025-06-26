# He'story - AI 기반 시니어 자서전 작성 서비스

## 🌟 프로젝트 개요

He'story는 시니어(아버지 세대)를 위한 AI 기반 자서전 작성 서비스입니다. **"기억의 안내자"**라는 전문 AI 인터뷰어와의 편안한 대화를 통해 삶의 이야기를 수집하고, 이를 바탕으로 개인의 자서전을 자동 생성합니다.

## ✨ 핵심 기능

### 🎤 AI 인터뷰 시스템
- **기억의 안내자**: 따뜻하고 공감적인 전문 AI 인터뷰어
- **실시간 음성 인터뷰**: Gemini Live API를 통한 자연스러운 대화
- **텍스트 인터뷰**: 웹 기반 채팅 인터페이스도 지원
- **지능적 대화 흐름**: 7가지 대화 원칙 기반 체계적 진행

### 📖 12개 구조화된 세션
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

### 👥 시니어 친화적 UI
- **큰 글씨**: 최소 18px, 제목은 24px 이상
- **높은 대비**: 명확한 색상 구분
- **직관적 버튼**: 최소 60px 높이의 터치하기 쉬운 인터페이스
- **간단한 네비게이션**: 3단계 이내 모든 기능 접근

### 🤖 AI 자서전 생성
- **전문 작가 프롬프트**: 체계적인 자서전 구성
- **1인칭 시점**: 자연스러운 개인 이야기 형태
- **완성된 초고**: 바로 읽고 공유 가능한 수준
- **다양한 내보내기**: 텍스트, PDF 형태 지원

## 🛠 기술 스택

### Backend
- **Framework**: FastAPI 0.109.0
- **Language**: Python 3.11+
- **AI**: Google Gemini API (Live API, Text Generation)
- **Database**: PostgreSQL + SQLAlchemy
- **Authentication**: JWT + OAuth2
- **Real-time**: WebSocket
- **Audio**: PyAudio

### Frontend
- **Framework**: React 18.2.0
- **Router**: React Router DOM 6.8.1
- **HTTP Client**: Axios 1.3.4
- **Icons**: Lucide React
- **Styling**: Custom CSS (시니어 친화적)
- **Font**: Noto Sans KR

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 15
- **Web Server**: Nginx (프론트엔드)
- **Deployment**: Docker-based

## 📁 프로젝트 구조

```
hestorygem/
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py            # FastAPI 애플리케이션
│   │   ├── models/            # 데이터베이스 모델
│   │   │   ├── session_templates.py  # 12개 세션 정의
│   │   │   ├── user.py
│   │   │   ├── session.py
│   │   │   └── conversation.py
│   │   ├── api/               # API 엔드포인트
│   │   │   ├── auth.py
│   │   │   ├── sessions.py
│   │   │   ├── conversations.py
│   │   │   └── autobiography.py
│   │   ├── services/          # 비즈니스 로직
│   │   │   ├── gemini_service.py
│   │   │   ├── interview_service.py
│   │   │   ├── conversation_manager.py
│   │   │   └── autobiography_service.py
│   │   └── db/                # 데이터베이스 설정
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
├── frontend/                   # React 프론트엔드
│   ├── src/
│   │   ├── App.js             # 메인 앱 컴포넌트
│   │   ├── pages/             # 페이지 컴포넌트
│   │   │   ├── LoginPage.js
│   │   │   ├── SessionListPage.js
│   │   │   ├── InterviewPage.js
│   │   │   ├── MyStoriesPage.js
│   │   │   └── AutobiographyPage.js
│   │   ├── components/        # 재사용 컴포넌트
│   │   ├── context/           # React Context
│   │   ├── services/          # API 통신
│   │   └── styles/            # 스타일링
│   ├── package.json
│   ├── Dockerfile
│   └── README.md
├── docker-compose.yml          # 전체 서비스 오케스트레이션
├── .env.example               # 환경 변수 템플릿
└── README.md                  # 이 파일
```

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone <repository-url>
cd hestorygem
```

### 2. 환경 변수 설정
```bash
cp .env.example .env
```

`.env` 파일에서 다음 설정:
```bash
# Google AI Studio에서 발급받은 API 키
GOOGLE_API_KEY=your_google_api_key_here

# 데이터베이스 설정
DATABASE_URL=postgresql://hestory:hestory123@db:5432/hestory

# JWT 시크릿 키
SECRET_KEY=your_jwt_secret_key_here
```

### 3. Docker Compose로 실행
```bash
# 전체 서비스 실행
docker-compose up

# 백그라운드 실행
docker-compose up -d
```

### 4. 서비스 접속
- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 🎯 사용자 시나리오

### 1. 회원가입 및 로그인
```
회원가입 → 12개 세션 자동 생성 → 로그인 → 세션 리스트
```

### 2. 인터뷰 진행
```
세션 선택 → 대화 시작하기 → AI 인사말 → 음성/텍스트 응답 → 자동 저장
```

### 3. 이야기 관리
```
내 이야기 보기 → 세션별 요약 확인 → 상세 대화 내용 → 데이터 내보내기
```

### 4. 자서전 생성
```
자서전 페이지 → 생성 가능 상태 확인 → 자서전 초고 만들기 → 완성된 자서전
```

## 🔧 개발 환경 설정

### 백엔드 개발
```bash
cd backend

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
uvicorn app.main:app --reload
```

### 프론트엔드 개발
```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm start
```

### 전체 개발 환경
```bash
# 개발용 Docker Compose (핫 리로드 지원)
docker-compose -f docker-compose.dev.yml up
```

## 📚 API 문서

### 주요 엔드포인트

#### 인증
- `POST /api/auth/register` - 회원가입
- `POST /api/auth/token` - 로그인
- `GET /api/auth/me` - 사용자 정보

#### 세션 관리
- `GET /api/sessions/` - 세션 목록
- `GET /api/sessions/{id}` - 세션 상세
- `GET /api/sessions/{id}/flow-status` - 대화 흐름 상태

#### 인터뷰
- `POST /api/conversations/interview` - 텍스트 인터뷰
- `WebSocket /api/conversations/live/{session_id}` - 실시간 음성 인터뷰

#### 자서전
- `POST /api/autobiography/generate` - 자서전 생성
- `GET /api/autobiography/status` - 생성 가능 상태

자세한 API 문서: http://localhost:8000/docs

## 🧪 테스트

### 백엔드 테스트
```bash
cd backend

# 시스템 테스트
python test_interview.py templates  # 세션 템플릿 확인
python test_interview.py manager   # 대화 관리자 테스트
python test_interview.py full      # 전체 플로우 테스트 (API 키 필요)
```

### 프론트엔드 테스트
```bash
cd frontend

# 단위 테스트
npm test

# E2E 테스트 (설정 필요)
npm run test:e2e
```

## 🌐 배포

### 프로덕션 배포
```bash
# 프로덕션 빌드
docker-compose -f docker-compose.prod.yml up --build

# 백그라운드 실행
docker-compose -f docker-compose.prod.yml up -d
```

### 개별 서비스 배포
```bash
# 백엔드만 배포
cd backend
docker build -t hestory-backend .
docker run -p 8000:8000 --env-file .env hestory-backend

# 프론트엔드만 배포
cd frontend
docker build -t hestory-frontend .
docker run -p 3000:3000 hestory-frontend
```

## 🔒 보안 고려사항

- **API 키 관리**: `.env` 파일로 민감 정보 분리
- **CORS 설정**: 허용된 출처만 API 접근 가능
- **JWT 토큰**: 안전한 사용자 인증
- **입력 검증**: 모든 사용자 입력 검증 및 sanitization

## 🐛 문제 해결

### 일반적인 문제

#### 음성 기능이 작동하지 않는 경우
- Chrome 브라우저 사용 확인
- HTTPS 환경 또는 localhost에서 실행
- 마이크 권한 허용 확인

#### API 연결 오류
- 백엔드 서버 실행 상태 확인: http://localhost:8000/health
- Google API 키 설정 확인
- 방화벽 및 네트워크 설정 확인

#### 데이터베이스 연결 오류
```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs db
docker-compose logs backend
```

### 로그 확인
```bash
# 전체 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🤝 기여 가이드

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- Google Gemini API 팀
- FastAPI 및 React 커뮤니티
- 모든 베타 테스터 분들

---

**He'story** - 소중한 인생 이야기를 영원히 기록하세요 📖✨