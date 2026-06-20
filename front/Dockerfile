# Node.js 가벼운 버전으로 베이스 이미지 가져오기
FROM node:20-alpine

# 상자 내부에서 작업할 폴더 지정
WORKDIR /app

# 라이브러리 설치를 위해 파일 복사 및 설치
COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

# 실행 명령어 (Vite가 제공하는 preview 서버를 모든 IP로 열어주기!)
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]