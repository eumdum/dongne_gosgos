# Node.js 가벼운 버전으로 베이스 이미지 가져오기
FROM node:20-alpine

# 상자 내부에서 작업할 폴더 지정
WORKDIR /app

# 라이브러리 설치를 위해 파일 복사 및 설치
COPY package*.json ./
RUN npm install

COPY . .

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

ARG VITE_KAKAO_MAP_KEY
ENV VITE_KAKAO_MAP_KEY=$VITE_KAKAO_MAP_KEY

ARG VITE_IMP_KEY
ENV VITE_IMP_KEY=$VITE_IMP_KEY

ARG VITE_CHANNEL_KEY
ENV VITE_CHANNEL_KEY=$VITE_CHANNEL_KEY

RUN npm run build
CMD ["npm", "run", "preview"]