#!/bin/sh
set -eu

###############################################################################
# 0) 필수 ENV 검사  (dash 호환)
###############################################################################
for key in INSTAGRAM_USERNAME INSTAGRAM_PASSWORD NEIS_API_KEY
do
  # printenv 가 변수 없으면 1을 반환하므로 ‘|| true’ 로 에러 무시
  val=$(printenv "$key" 2>/dev/null || true)
  if [ -z "$val" ]; then
    echo "[entrypoint] FATAL: $key is not set"; exit 1
  fi
done

###############################################################################
# 1) 세션 디렉터리 보장
###############################################################################
mkdir -p /app/ig_session && chmod 700 /app/ig_session

###############################################################################
# 2) cron·시스템 전역 ENV 등록
#    /etc/environment 은 root 크론에도 자동 로드됨
###############################################################################
{
  echo "INSTAGRAM_USERNAME=${INSTAGRAM_USERNAME}"
  echo "INSTAGRAM_PASSWORD=${INSTAGRAM_PASSWORD}"
  echo "NEIS_API_KEY=${NEIS_API_KEY}"
  echo "TZ=Asia/Seoul"
} >> /etc/environment

###############################################################################
# 3) django‑crontab 등록 / 갱신
###############################################################################
python3 manage.py crontab remove || true
python3 manage.py crontab add

###############################################################################
# 4) cron 데몬 실행 (백그라운드)
###############################################################################
/usr/sbin/cron -f &
echo "[entrypoint] cron started (pid=$!)"

###############################################################################
# 5) Django runserver (포그라운드, PID 1 유지)
###############################################################################
exec python3 manage.py runserver 0.0.0.0:8857