
# kshs_insta

  

강원과학고등학교 급식 정보를 NEIS Open API로 가져와 자동으로 인스타그램 스토리에 업로드하는 Django 프로젝트입니다.


# 사용시 env를 .env로 바꿔줘야함!!! 그래야 환경변수로 잘 인식함

  

## 주요 기능

- NEIS API를 이용해 조식·중식·석식 메뉴를 조회

- 예쁜 배경 이미지 위에 한글 폰트로 메뉴 텍스트 렌더링

- 알레르기 정보를 자동 파싱하여 메뉴 하단에 표시

-  `django-crontab`을 이용해 매일 지정 시간에 자동 업로드

- 수동 테스트용 HTTP 엔드포인트 제공

  

## 요구 사항

- Python 3.10+

- Django 5.2

- requests

- Pillow

- django-crontab

- instagrapi (인스타그램 업로드용)

- python-decouple (환경 변수 로드)

  

## 설치 및 실행

  

1. 저장소 클론

```bash

git clone https://github.com/your-username/kshs_insta.git

cd kshs_insta

```

  

2. 가상환경 생성 및 활성화

```bash

python3  -m  venv  .venv

source  .venv/bin/activate

```

  

3. 패키지 설치

```bash

pip  install  -r  requirements.txt

```

  

4. 환경 변수 설정

프로젝트 루트에 .env 파일을 생성하고 아래 항목을 추가하세요:

```bash

INSTAGRAM_USERNAME=your_instagram_id

INSTAGRAM_PASSWORD=your_instagram_password

NEIS_API_KEY=your_neis_service_key

```

  

5. static·media 디렉터리 생성

```bash

mkdir  -p  static/bg  static/fonts  media/menus

```

  

6. 폰트 및 배경 이미지 복사

- static/bg/menu_bg_allergy.png : 배경 이미지

- static/fonts/ 아래에 한글 TTF/OTF 폰트 파일 추가

- NotoSansKR-Bold.otf

- NotoSansKR-Medium.otf

- NotoSansKR-Regular.otf

  

7. Django 마이그레이션 (필요 시)

```bash

python  manage.py  migrate

```

  

8. 개발 서버 실행

```bash

python  manage.py  runserver

```

  
  

## 사용방법

  

수동 업로드 테스트

  

브라우저 또는 curl을 통해 아래 엔드포인트를 호출:

  

    GET /meals/upload/?meal_type=<breakfast|lunch|dinner>&date=YYYYMMDD

  

예:

  

    http://127.0.0.1:8000/meals/upload/?meal_type=lunch&date=20250503

  

예약된 자동 업로드

  

django-crontab 설정에 따라 매일 조식·중식·석식이 자동 업로드됩니다.

1. 크론잡 등록

  
```bash
python manage.py crontab add
```
  
  

2. 등록된 잡 확인

  

```bash
python manage.py crontab show
```
  
  

3. 크론잡 제거

  

```bash
python manage.py crontab remove
```

## 커스터마이징

• 이미지 템플릿

static/bg/menu_bg_allergy.png를 교체하면 배경 디자인을 변경할 수 있습니다.

• 폰트 변경

static/fonts/ 폴더의 폰트 파일 및 meals/image.py에서 지정한 폰트 경로를 수정하세요.

• 레이아웃 조정

meals/image.py의 좌표(y=560/title, y=730/menu, y=1520/allergy) 및 x_start, max_width 값을 변경해 텍스트 배치를 조절할 수 있습니다.

  

## 라이선스
MIT License

