# 1단계: 빌드 환경
FROM node:20-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# 빌드 시점 환경 변수 주입
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

ARG VITE_KAKAO_MAP_KEY
ENV VITE_KAKAO_MAP_KEY=$VITE_KAKAO_MAP_KEY

ARG VITE_IMP_KEY
ENV VITE_IMP_KEY=$VITE_IMP_KEY

ARG VITE_CHANNEL_KEY
ENV VITE_CHANNEL_KEY=$VITE_CHANNEL_KEY

ARG VITE_SGIS_SERVICE_ID
ENV VITE_SGIS_SERVICE_ID=$VITE_SGIS_SERVICE_ID

ARG VITE_SGIS_SECURITY_KEY
ENV VITE_SGIS_SECURITY_KEY=$VITE_SGIS_SECURITY_KEY

RUN npm run build

# 2단계: Nginx 경량화 실행 환경
FROM nginx:alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
# 프로젝트에 만든 default.conf 복사
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# # Node.js 가벼운 버전으로 베이스 이미지 가져오기
# FROM node:20-alpine

# # 상자 내부에서 작업할 폴더 지정
# WORKDIR /app

# # 라이브러리 설치를 위해 파일 복사 및 설치
# COPY package*.json ./
# RUN npm install

# COPY . .

# ARG VITE_API_URL
# ENV VITE_API_URL=$VITE_API_URL

# ARG VITE_KAKAO_MAP_KEY
# ENV VITE_KAKAO_MAP_KEY=$VITE_KAKAO_MAP_KEY

# ARG VITE_IMP_KEY
# ENV VITE_IMP_KEY=$VITE_IMP_KEY

# ARG VITE_CHANNEL_KEY
# ENV VITE_CHANNEL_KEY=$VITE_CHANNEL_KEY

# RUN npm run build
# CMD ["npx", "vite", "preview", "--host", "0.0.0.0", "--port", "3000"]