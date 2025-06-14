# Dockerfile

FROM python:3.11-slim

# 환경 변수 설정 
# 여기에 인스타그램 아이디와 비번 쓰고, 나이스 급식 정보 받는 API키 받아서 써놔야함
# 만약에 django를 외부에서도 접속가능하게 웹사이트로 만들어서 띠울거라면 그 도메인도 써줘야함 저 밑에 장고 어로우드 호스트에 sivelop.com 이런식으로
ENV PYTHONUNBUFFERED=1
ENV INSTAGRAM_USERNAME=kshs__official
ENV INSTAGRAM_PASSWORD=
ENV NEIS_API_KEY=
ENV DJANGO_ALLOWED_HOSTS=

WORKDIR /app

# 1) 시스템 패키지 설치: cron + tzdata + Pillow 의존성
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      cron tzdata libjpeg-dev zlib1g-dev && \
    # 타임존 설정
    ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo "Asia/Seoul" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# 2) Python 의존성 설치
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 3) 애플리케이션 소스 복사
COPY . .

# 4) 엔트리포인트 스크립트 복사
COPY deploy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 5) 외부에 노출할 포트
EXPOSE 8857

# 6) 컨테이너 시작 시 스크립트 실행
ENTRYPOINT ["/entrypoint.sh"]