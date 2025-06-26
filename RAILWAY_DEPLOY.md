# Railway 배포 가이드

## 🚀 He'story Railway 배포 방법

### 1. 백엔드 배포 (우선)

#### A. GitHub에서 직접 배포 (권장)
1. Railway 대시보드에서 "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. `ddoriboo/hestorygem` repository 선택
4. "Deploy Now" 클릭

#### B. Railway CLI로 배포
```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 초기화
railway init

# 배포
railway up
```

### 2. 환경 변수 설정

Railway 대시보드에서 다음 환경 변수들을 설정하세요:

#### 필수 환경 변수
```
GOOGLE_API_KEY=your_google_api_key_here
SECRET_KEY=your_jwt_secret_key_here
ENVIRONMENT=production
```

#### 데이터베이스 설정 (Railway PostgreSQL 플러그인 사용)
```
DATABASE_URL=postgresql://username:password@host:port/database
```

### 3. Railway PostgreSQL 데이터베이스 추가

1. 프로젝트 대시보드에서 "Add Plugin" 클릭
2. "PostgreSQL" 선택
3. 자동으로 `DATABASE_URL` 환경 변수가 설정됨

### 4. 배포 설정

#### 방법 1: Root 레벨 배포 (현재 설정)
- `main.py`: Railway용 진입점
- `requirements.txt`: 의존성 목록
- `Procfile`: 웹 서버 실행 명령
- `runtime.txt`: Python 버전 지정

#### 방법 2: 서비스 분리 배포
백엔드와 프론트엔드를 별도 서비스로 배포:

```bash
# 백엔드용 별도 Repository 생성
git subtree push --prefix=backend origin backend-deploy

# 프론트엔드용 별도 Repository 생성  
git subtree push --prefix=frontend origin frontend-deploy
```

### 5. 배포 후 확인사항

#### 백엔드 API 테스트
```bash
# 헬스 체크
curl https://your-railway-url.railway.app/health

# API 문서 확인
https://your-railway-url.railway.app/docs
```

#### 데이터베이스 연결 확인
```bash
# Railway CLI로 로그 확인
railway logs

# PostgreSQL 연결 상태 확인
railway connect postgres
```

### 6. 프론트엔드 배포 (Vercel 권장)

백엔드가 Railway에 배포된 후, 프론트엔드는 Vercel에 배포하는 것을 권장:

1. Vercel에 `frontend/` 폴더 배포
2. 환경 변수 설정:
   ```
   REACT_APP_API_URL=https://your-railway-backend-url.railway.app
   ```

### 7. 도메인 설정

#### Railway 도메인
- 자동 생성: `your-app-name.railway.app`
- 커스텀 도메인: Settings → Domains

#### CORS 설정 업데이트
백엔드의 `backend/app/config.py`에서 프론트엔드 도메인 추가:
```python
backend_cors_origins: list = [
    "http://localhost:3000",
    "https://your-frontend-domain.vercel.app",
    "https://your-custom-domain.com"
]
```

### 8. 문제 해결

#### 일반적인 오류들

1. **Nixpacks build failed**
   - `requirements.txt`가 루트에 있는지 확인
   - Python 런타임 버전 확인 (`runtime.txt`)

2. **Module not found**
   - `main.py`의 import 경로 확인
   - 패키지 구조 검증

3. **Database connection error**
   - `DATABASE_URL` 환경 변수 확인
   - PostgreSQL 플러그인 상태 확인

4. **API Key error**
   - `GOOGLE_API_KEY` 환경 변수 설정 확인
   - Google AI Studio에서 API 키 활성화 상태 확인

#### 로그 확인
```bash
# Railway CLI로 실시간 로그 확인
railway logs --follow

# 특정 서비스 로그
railway logs --service backend
```

### 9. 추가 최적화

#### 성능 최적화
- Railway Pro 플랜으로 업그레이드 (더 많은 리소스)
- Redis 캐시 추가 (Railway Redis 플러그인)
- CDN 설정 (Cloudflare 등)

#### 모니터링
- Railway 대시보드에서 CPU/메모리 사용량 확인
- 로그 모니터링으로 에러 추적
- 업타임 모니터링 설정

### 10. 비용 관리

#### Railway 요금제
- **Hobby**: $5/월 (500시간 실행 시간)
- **Pro**: $20/월 (무제한 실행 시간)

#### 최적화 팁
- 사용하지 않는 서비스는 일시 중지
- 개발 환경과 프로덕션 환경 분리
- 필요에 따라 스케일링 조정

---

## 🎯 권장 배포 전략

1. **백엔드**: Railway (Python/FastAPI 특화)
2. **프론트엔드**: Vercel (React 특화)
3. **데이터베이스**: Railway PostgreSQL
4. **파일 저장소**: Railway 또는 AWS S3

이렇게 하면 각 서비스의 장점을 최대화하면서 안정적인 운영이 가능합니다.