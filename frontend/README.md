# He'story Frontend

AI 기반 시니어 자서전 작성 서비스의 React 프론트엔드입니다.

## 주요 기능

### 🎯 시니어 친화적 디자인
- **큰 글씨**: 최소 18px, 제목은 24px 이상
- **높은 대비**: 명확한 검정/흰색 기반 색상
- **큰 버튼**: 최소 60px 높이의 터치하기 쉬운 버튼
- **직관적 네비게이션**: 간단하고 명확한 메뉴 구조

### 📱 페이지 구성
1. **로그인/회원가입**: 간단한 인증 시스템
2. **세션 리스트**: 12개 인생 이야기 세션 관리
3. **인터뷰 페이지**: 실시간 음성/텍스트 인터뷰
4. **내 이야기 보기**: 세션별 대화 내용 및 요약
5. **자서전 페이지**: AI 기반 자서전 초고 생성

### 🎤 음성 인터뷰 기능
- **웹 음성 인식**: 브라우저 내장 Speech Recognition API 활용
- **음성 합성**: AI 응답을 음성으로 재생
- **실시간 텍스트 변환**: 음성이 실시간으로 텍스트로 변환
- **혼합 모드**: 음성과 텍스트 입력을 자유롭게 전환

## 기술 스택

- **Framework**: React 18.2.0
- **Router**: React Router DOM 6.8.1
- **HTTP Client**: Axios 1.3.4
- **Icons**: Lucide React 0.321.0
- **Styling**: Custom CSS with CSS Variables
- **Font**: Noto Sans KR (한글 최적화)

## 설치 및 실행

### 개발 환경
```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm start

# 브라우저에서 http://localhost:3000 접속
```

### 프로덕션 빌드
```bash
# 빌드
npm run build

# 빌드된 파일들이 build/ 폴더에 생성됨
```

### Docker 실행
```bash
# Docker 이미지 빌드
docker build -t hestory-frontend .

# 컨테이너 실행
docker run -p 3000:3000 hestory-frontend
```

## 환경 변수

`.env` 파일을 생성하여 설정:

```bash
# 백엔드 API URL
REACT_APP_API_URL=http://localhost:8000

# 기타 설정
REACT_APP_VERSION=1.0.0
```

## 사용자 플로우

### 1. 온보딩
```
로그인/회원가입 → 12개 세션 자동 생성 → 세션 리스트 화면
```

### 2. 인터뷰 진행
```
세션 선택 → 대화 시작 버튼 → AI 인사말 → 음성/텍스트 응답 → 자동 저장
```

### 3. 자서전 생성
```
내 이야기 보기 → 충분한 대화 축적 → 자서전 초고 만들기 → 완성된 자서전
```

## 컴포넌트 구조

```
src/
├── App.js                 # 메인 앱 컴포넌트 및 라우팅
├── context/
│   └── AuthContext.js     # 사용자 인증 상태 관리
├── services/
│   └── api.js             # 백엔드 API 통신
├── components/
│   ├── Layout.js          # 전체 레이아웃 (헤더, 네비게이션)
│   └── LoadingSpinner.js  # 로딩 스피너
├── pages/
│   ├── LoginPage.js       # 로그인 페이지
│   ├── RegisterPage.js    # 회원가입 페이지
│   ├── SessionListPage.js # 세션 목록 페이지
│   ├── InterviewPage.js   # 인터뷰 진행 페이지
│   ├── MyStoriesPage.js   # 내 이야기 보기 페이지
│   └── AutobiographyPage.js # 자서전 생성 페이지
└── styles/
    └── global.css         # 글로벌 스타일 (시니어 친화적)
```

## API 통신

### 인증
- `POST /api/auth/login` - 로그인
- `POST /api/auth/register` - 회원가입
- `GET /api/auth/me` - 사용자 정보

### 세션 관리
- `GET /api/sessions/` - 세션 목록
- `GET /api/sessions/{id}` - 세션 상세
- `PATCH /api/sessions/{id}` - 세션 상태 업데이트

### 대화 관리
- `GET /api/conversations/session/{session_id}` - 세션별 대화 목록
- `POST /api/conversations/interview` - 텍스트 인터뷰
- `WebSocket /api/conversations/live/{session_id}` - 실시간 음성 인터뷰

### 자서전
- `POST /api/autobiography/generate` - 자서전 생성
- `GET /api/autobiography/status` - 생성 가능 상태

## 접근성 및 사용성

### 시니어 친화적 설계
- **대형 UI 요소**: 모든 버튼과 입력 필드가 충분히 큼
- **명확한 피드백**: 로딩, 성공, 오류 상태를 명확히 표시
- **간단한 네비게이션**: 3단계 이내로 모든 기능 접근 가능
- **음성 지원**: 타이핑이 어려운 사용자를 위한 음성 입력

### 브라우저 호환성
- **권장 브라우저**: Chrome, Edge (음성 기능 지원)
- **최소 요구사항**: 모던 브라우저 (ES6+ 지원)
- **반응형**: 데스크톱, 태블릿 화면 최적화

## 개발 가이드

### 새로운 페이지 추가
1. `src/pages/` 에 새 컴포넌트 생성
2. `App.js`에서 라우트 추가
3. 필요시 `Layout.js`의 네비게이션 업데이트

### 스타일 수정
- 시니어 친화적 스타일: `src/styles/global.css`
- CSS 변수 활용으로 일관된 디자인 유지
- 최소 글자 크기 18px, 버튼 높이 60px 준수

### API 연동
- `src/services/api.js`에서 새 API 메서드 추가
- 인증이 필요한 경우 자동으로 토큰 헤더 추가
- 에러 처리 및 로딩 상태 관리 필수

## 빌드 및 배포

### 정적 파일 배포
```bash
npm run build
# build/ 폴더를 웹 서버에 배포
```

### Docker 배포
```bash
docker build -t hestory-frontend .
docker run -p 3000:3000 -e REACT_APP_API_URL=https://api.hestory.com hestory-frontend
```

### CDN 최적화
- 빌드 시 자동으로 코드 분할 및 압축
- 이미지 최적화 권장
- Gzip 압축 활성화 (nginx.conf 설정)

## 문제 해결

### 음성 기능이 작동하지 않는 경우
- Chrome 브라우저 사용 확인
- HTTPS 환경에서 실행 (로컬은 localhost 허용)
- 마이크 권한 허용 확인

### API 연결 오류
- 백엔드 서버 실행 상태 확인
- CORS 설정 확인
- 네트워크 방화벽 설정 확인

### 빌드 오류
```bash
# 캐시 삭제 후 재시도
npm run build -- --clean-cache
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 라이선스

MIT License - 자세한 내용은 LICENSE 파일을 참조하세요.