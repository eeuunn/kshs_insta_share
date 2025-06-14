# meals/utils.py

import requests
from datetime import date
from django.conf import settings

# 식사 종류 ↔ NEIS API 식사코드 매핑
MEAL_TYPE_MAP = {
    'breakfast': '1',  # 조식
    'lunch':     '2',  # 중식
    'dinner':    '3',  # 석식
}

def fetch_menu_for_date(meal_type: str, target_date: date) -> str:
    """
    동기 방식으로 NEIS Open API 호출.
    meal_type: 'breakfast'|'lunch'|'dinner'
    target_date: datetime.date 객체

    반환: 해당 날짜·식사 메뉴 문자열 (없으면 안내 문구)
    """
    # 0) 파라미터 준비
    ymd = target_date.strftime("%Y%m%d")
    mmeal_sc = MEAL_TYPE_MAP.get(meal_type)
    if not mmeal_sc:
        return "메뉴 정보가 없습니다."

    # 1) API 엔드포인트 & 기본 인자
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "KEY":      settings.NEIS_API_KEY,  # 발급받은 서비스 키
        "Type":     "json",                 # 응답 포맷
        "pIndex":   1,                      # 페이지 위치 (정수)
        "pSize":    100,                    # 페이지 당 건수 (정수)
        "ATPT_OFCDC_SC_CODE": None,         # 아래에서 채움
        "SD_SCHUL_CODE":       None,        # 아래에서 채움
        "MMEAL_SC_CODE":       mmeal_sc,    # 식사코드 ('1','2','3')
        "MLSV_YMD":            ymd,         # 조회 날짜 'YYYYMMDD'
    }

    try:
        # 2) 먼저 학교 코드 조회
        school_url = "https://open.neis.go.kr/hub/schoolInfo"
        school_params = {
            "KEY":    settings.NEIS_API_KEY,
            "Type":   "json",
            "pIndex": 1,
            "pSize":  10,
            "SCHUL_NM":"강원과학고등학교",
        }
        r = requests.get(school_url, params=school_params)
        r.raise_for_status()
        j = r.json()
        info = j['schoolInfo'][1]['row'][0]
        params["ATPT_OFCDC_SC_CODE"] = info['ATPT_OFCDC_SC_CODE']
        params["SD_SCHUL_CODE"]       = info['SD_SCHUL_CODE']

        # 3) 급식 정보 요청
        r2 = requests.get(url, params=params)
        r2.raise_for_status()
        j2 = r2.json()

        # 4) 결과 파싱
        #    필드명이 'mealServiceDietInfo'
        data = j2.get('mealServiceDietInfo')
        if not data or len(data) < 2:
            return "메뉴 정보가 없습니다."

        rows = data[1].get('row', [])
        if not rows:
            return "메뉴 정보가 없습니다."

        # 첫 번째 항목
        item = rows[0]
        # DDISH_NM 에 메뉴가 <br/>로 구분돼 있으니 \n 처리
        return item.get('DDISH_NM', '').replace('<br/>', '\n') or "메뉴 정보가 없습니다."

    except Exception as e:
        # 인증키 오류, 네트워크 오류, JSON 파싱 오류 등
        print(f"🛑 fetch_menu_for_date error ({ymd}, {meal_type}):", e)
        return "메뉴 정보가 없습니다."