FROM node:18-alpine

WORKDIR /app

# 패키지 파일 복사 및 의존성 설치
COPY package*.json ./
RUN npm ci --only=production

# 소스 코드 복사
COPY . .

# 환경 변수
ENV REACT_APP_API_URL=http://localhost:8000

# 빌드
RUN npm run build

# Nginx로 정적 파일 서빙
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html

# Nginx 설정 (React Router를 위한 설정)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]