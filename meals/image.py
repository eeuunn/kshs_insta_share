# meals/image.py

import os
import re
from datetime import date
from datetime import date as _date
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

# 영어 식사 코드 → 한글 표시명 매핑
KOREAN_MEAL_LABEL = {
    'breakfast': '아침',
    'lunch':     '점심',
    'dinner':    '저녁',
}

# 알레르기 번호 → 한글 재료명 매핑
ALLERGY_MAP = {
    '1': '난류',   '2': '우유',   '3': '메밀', '4': '땅콩',
    '5': '대두',   '6': '밀',     '7': '고등어','8': '게',
    '9': '새우',  '10': '돼지고기','11': '복숭아','12': '토마토',
   '13': '아황산류','14': '호두',  '15': '닭고기','16': '쇠고기',
   '17': '오징어','18': '조개류', '19': '잣',
}

def render_menu_image(text: str, meal_type: str, target_date: _date) -> str:
    # 1) 배경 열기
    bg_path = os.path.join(settings.BASE_DIR, 'static', 'bg', 'menu_bg_allergy.png')
    base    = Image.open(bg_path).convert("RGBA")
    width, height = base.size

    # 2) 폰트 준비
    title_font   = ImageFont.truetype(
        os.path.join(settings.BASE_DIR, 'static', 'fonts', 'NotoSansKR-Bold.ttf'),
        size=48
    )
    menu_font    = ImageFont.truetype(
        os.path.join(settings.BASE_DIR, 'static', 'fonts', 'NotoSansKR-Medium.ttf'),
        size=48
    )
    allergy_font = ImageFont.truetype(
        os.path.join(settings.BASE_DIR, 'static', 'fonts', 'NotoSansKR-Regular.ttf'),
        size=36
    )

    # 3) 드로어 준비
    txt_layer = Image.new("RGBA", base.size, (255,255,255,0))
    draw      = ImageDraw.Draw(txt_layer)

    # 4) 제목 그리기 (y=560px)
    korean_label = KOREAN_MEAL_LABEL.get(meal_type, meal_type)
    title_text   = f"{target_date.strftime('%Y-%m-%d')} {korean_label}"
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_w, title_h = bbox[2]-bbox[0], bbox[3]-bbox[1]
    x_title = (width - title_w) / 2
    y_title = 560
    draw.text((x_title, y_title), title_text, font=title_font, fill=(0,0,0,255))

    # 5) 메뉴 본문 그리기 (y=730px부터, x=140~940px)
    x_start, x_end = 140, 940
    max_width      = x_end - x_start
    y = 730

    def wrap_text(line: str, font):
        wrapped, curr = [], ""
        for ch in line:
            test = curr + ch
            b = draw.textbbox((0,0), test, font=font)
            if b[2]-b[0] <= max_width:
                curr = test
            else:
                wrapped.append(curr)
                curr = ch
        if curr:
            wrapped.append(curr)
        return wrapped

    for orig in text.split("\n"):
        for line in wrap_text(orig, menu_font):
            b = draw.textbbox((0,0), line, font=menu_font)
            line_w, line_h = b[2]-b[0], b[3]-b[1]
            x_line = (width - line_w) / 2
            draw.text((x_line, y), line, font=menu_font, fill=(0,0,0,255))
            y += line_h + 10

        # 6) 알레르기 정보 파싱
    codes = []
    for orig in text.split("\n"):
        for match in re.findall(r'\(([\d\.]+)\)', orig):
            for num in match.split('.'):
                if num in ALLERGY_MAP and num not in codes:
                    codes.append(num)

    # 7) 알레르기 정보 그리기 (y=1510px부터, 한 줄에 "알레르기 정보: 1. 난류, 2. 우유…" 형태로,
    #    마지막에는 쉼표 없이, 영역 초과 시 아이템 단위로 wrap)
    if codes:
        y_allergy = 1510
        x_start   = 140
        max_width = 940 - x_start

        # 7-1) 아이템 문자열 리스트
        items = [f"{num}. {ALLERGY_MAP[num]}" for num in sorted(codes, key=int)]

        # 7-2) inline wrap
        line = "알레르기 정보: "
        for idx, item in enumerate(items):
            # 마지막 항목이면 쉼표 생략
            token = item + (", " if idx < len(items)-1 else "")
            test  = line + token
            tb    = draw.textbbox((0, 0), test, font=allergy_font)
            if tb[2] - tb[0] <= max_width:
                line = test
            else:
                # 현재까지 쌓인 line 출력
                draw.text((x_start, y_allergy), line, font=allergy_font, fill=(0,0,0,255))
                # 다음 줄로 이동
                hb = draw.textbbox((0, 0), line, font=allergy_font)
                y_allergy += (hb[3] - hb[1]) + 5
                # 새로운 줄은 token부터 시작
                line = token

        # 7-3) 마지막 줄 출력
        if line:
            draw.text((x_start, y_allergy), line, font=allergy_font, fill=(0,0,0,255))

    # 8) 합성 및 저장
    out = Image.alpha_composite(base, txt_layer).convert("RGB")
    out_dir = os.path.join(settings.BASE_DIR, 'media', 'menus')
    os.makedirs(out_dir, exist_ok=True)
    filename = f"menu_{target_date.strftime('%Y%m%d')}_{meal_type}.png"
    path     = os.path.join(out_dir, filename)
    out.save(path, format="PNG")
    return path