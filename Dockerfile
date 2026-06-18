FROM python:3.12-slim

# 파이썬이 터미널 로그를 실시간으로 뿜어내도록 설정
ENV PYTHONUNBUFFERED=1

# 도커 컴퓨터 내부의 기본 작업 폴더 설정
WORKDIR /app

# 필수 설치 리스트
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/