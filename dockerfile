# Python 3.9 기반 경량 이미지 사용
FROM python:3.9-slim

# 컨테이너 내부 작업 디렉토리 설정
WORKDIR /app

# 필요한 빌드 도구 설치
RUN apt-get update && apt-get install -y \
    gcc \
    libasound2-dev \
    portaudio19-dev \
    && apt-get clean

# requirements.txt 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 소스 코드 복사
COPY . .

# Uvicorn을 통해 FastAPI 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
