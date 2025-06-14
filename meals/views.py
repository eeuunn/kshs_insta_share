# meals/views.py

import logging
from datetime import datetime, date
from django.http import HttpResponse
from .utils import fetch_menu_for_date
from .services import upload_menu_story

logger = logging.getLogger(__name__)

def upload_story(request):
    """
    GET 파라미터:
      - meal_type: 'breakfast'|'lunch'|'dinner' (기본 'lunch')
      - date     : YYYYMMDD (기본 오늘)

    서비스 호출 후 HTTP 응답 반환
    """
    meal_type = request.GET.get('meal_type', 'lunch')
    date_str  = request.GET.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y%m%d").date()
        except ValueError:
            return HttpResponse("date 형식 오류(YYYYMMDD)", status=400)
    else:
        target_date = date.today()

    logger.info("upload_story 요청: meal_type=%s, date=%s", meal_type, target_date)

    success = upload_menu_story(meal_type, target_date)
    if success:
        return HttpResponse(
            f"'{meal_type}' 메뉴({target_date}) 스토리 업로드 완료",
            status=200,
            content_type="text/plain; charset=utf-8"
        )
    else:
        return HttpResponse(
            "스토리 업로드 실패 (로그 확인)",
            status=500,
            content_type="text/plain; charset=utf-8"
        )

def test_menu(request):
    """
    ?date=YYYYMMDD 로 임의 날짜 조회. 없으면 오늘.
    """
    q = request.GET.get('date')
    try:
        target = datetime.strptime(q, "%Y%m%d").date() if q else date.today()
    except ValueError:
        return HttpResponse("date 형식 오류(YYYYMMDD)", status=400)

    breakfast = fetch_menu_for_date('breakfast', target)
    lunch     = fetch_menu_for_date('lunch',     target)
    dinner    = fetch_menu_for_date('dinner',    target)

    content = (
        f"=== {target} 급식 메뉴 (강원과학고) ===\n\n"
        f"▶ 조식:\n{breakfast}\n\n"
        f"▶ 중식:\n{lunch}\n\n"
        f"▶ 석식:\n{dinner}"
    )
    return HttpResponse(content, content_type="text/plain; charset=utf-8")