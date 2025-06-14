# meals/services.py

import os, json, logging, random, time
from datetime import date, timedelta

from django.conf import settings
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError
from .utils import fetch_menu_for_date
from .image import render_menu_image
from datetime import datetime, date

logger = logging.getLogger(__name__)

# instagrapi Client 생성 + 세션 유지
def get_client() -> Client:
    cl = Client()
    sfile = settings.IG_SESSION_FILE

    # (1) 기존 세션 로드
    if sfile.exists():
        try:
            cl.load_settings(sfile)
            cl.login(settings.INSTAGRAM_USERNAME,
                     settings.INSTAGRAM_PASSWORD,
                     reauth=False)              # 재로그인 패스
            logging.getLogger(__name__).info("기존 세션 재사용 성공")
            return cl
        except Exception as e:
            logging.getLogger(__name__).warning("세션 재사용 실패 → 재로그인: %s", e)

    # (2) 재로그인
    cl.login(settings.INSTAGRAM_USERNAME, settings.INSTAGRAM_PASSWORD)
    cl.dump_settings(sfile)                      # 새 세션 저장
    logging.getLogger(__name__).info("새 세션 저장: %s", sfile)
    return cl

# 이전에 올린 story PK를 저장할 파일
LAST_STORY_FILE = os.path.join(settings.BASE_DIR, "last_story.json")

def _load_last_ids() -> dict:
    """파일에서 {meal_type: story_pk} 맵을 불러옵니다."""
    if os.path.exists(LAST_STORY_FILE):
        try:
            return json.load(open(LAST_STORY_FILE, encoding="utf8"))
        except Exception:
            logger.warning("last_story.json 파싱 실패, 초기화합니다.")
    return {}

def _save_last_ids(data: dict):
    """{meal_type: story_pk} 맵을 파일에 저장합니다."""
    with open(LAST_STORY_FILE, "w", encoding="utf8") as f:
        json.dump(data, f)

def upload_menu_story(meal_type: str, target_date: date | None = None) -> bool:
    """
    meal_type: 'breakfast'|'lunch'|'dinner'
    target_date: 조회할 날짜. None이면 breakfast→내일, 나머지→오늘.
    오직 하나의 스토리만 남기도록 이전 스토리 모두 삭제.
    """
    # 1) 날짜 결정
    if target_date is None:
        target_date = (
            date.today() + timedelta(days=1)
            if meal_type == "breakfast"
            else date.today()
        )
    logger.info("업로드 시작: meal_type=%s, date=%s", meal_type, target_date)

    # 2) 메뉴 조회
    try:
        menu_text = fetch_menu_for_date(meal_type, target_date)
        # 급식 정보가 아예 없거나 안내 문구가 포함돼 있으면 업로드 X
        if not menu_text or "메뉴 정보가 없습니다" in menu_text:
            logger.info("급식 정보 없음 → 업로드 생략 (meal_type=%s, date=%s)",
                        meal_type, target_date)
            return False
        logger.debug("메뉴 조회 성공")
    except Exception as e:
        logger.error("메뉴 조회 실패: %s", e)
        return False

    # 3) 이미지 생성
    try:
        img_path = render_menu_image(menu_text, meal_type, target_date)
        logger.debug("이미지 생성 성공: %s", img_path)
    except Exception as e:
        logger.error("이미지 생성 실패: %s", e)
        return False

    # 4) Instagram 로그인
    try:
        cl = get_client()
        logger.info("Instagram 로그인 성공")
    except LoginRequired as e:
        logger.error("로그인 필요: %s", e)
        os.remove(img_path)
        return False
    except Exception as e:
        logger.error("로그인 실패: %s", e)
        os.remove(img_path)
        return False

    # 5) 이전에 올린 모든 스토리 삭제
    last_ids = _load_last_ids()
    for prev_meal, prev_pk in list(last_ids.items()):
        try:
            cl.story_delete(prev_pk)
            logger.info("이전 스토리 삭제 (%s): %s", prev_meal, prev_pk)
            # 삭제‑마다 1‑5 초 랜덤 휴식
            time.sleep(random.uniform(1, 5))
        except ClientError as e:
            logger.warning("이전 스토리 삭제 실패 (%s): %s", prev_meal, e)
        except Exception as e:
            logger.warning("이전 스토리 삭제 중 오류 (%s): %s", prev_meal, e)
        # 삭제 시도 후 기록에서도 제거
        last_ids.pop(prev_meal, None)
        # 삭제를 모두 끝낸 후에도 1‑5 초 휴식
        time.sleep(random.uniform(1, 5))

    # 6) 새 스토리 업로드
    try:
        caption = f"{target_date.strftime('%Y-%m-%d')} 급식 메뉴\n{menu_text}"
        story = cl.photo_upload_to_story(img_path, caption=caption)
        new_pk = story.pk
        logger.info("새 스토리 업로드 완료 (%s): %s", meal_type, new_pk)

        # 7) 현재 meal_type PK 저장
        last_ids[meal_type] = new_pk
        _save_last_ids(last_ids)
    except Exception as e:
        logger.error("스토리 업로드 실패: %s", e)
        os.remove(img_path)
        return False
    finally:
        # 8) 임시 이미지 삭제
        try:
            os.remove(img_path)
            logger.debug("임시 이미지 삭제")
        except OSError as e:
            logger.warning("임시 이미지 삭제 실패: %s", e)

    return True

# 지터(jitter) 래퍼 – 최대 1 시간 앞당기기
# (0 ~ 3600 초 랜덤 슬립 후 upload)
JITTER_SEC = 1 * 60 * 60      # 1 h

def _run_with_jitter(upload_fn):
    delay = random.randint(0, JITTER_SEC)
    logging.getLogger(__name__).info("⏳ 지터 %d 초 후 실행", delay)
    time.sleep(delay)
    return upload_fn()

# cron 이 호출할 래퍼
def upload_breakfast(): return _run_with_jitter(
        lambda: upload_menu_story('breakfast'))
def upload_lunch():     return _run_with_jitter(
        lambda: upload_menu_story('lunch'))
def upload_dinner():    return _run_with_jitter(
        lambda: upload_menu_story('dinner'))