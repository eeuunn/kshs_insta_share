import os
from pathlib import Path
from dotenv import load_dotenv
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=False)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'asdasdasdasdasd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'meals',
    'django_crontab',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kshs_insta.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'kshs_insta.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ——————————————————————————————————————
# 환경 변수
# ——————————————————————————————————————
INSTAGRAM_USERNAME = config('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = config('INSTAGRAM_PASSWORD')
NEIS_API_KEY = config('NEIS_API_KEY')

# ——————————————————————————————————————
# 미디어(업로드) 파일
# —————————————————————————————————————-
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# —————————————————————————————
# static files
# —————————————————————————————
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# instagrapi 세션 파일(호스트 ↔ 컨테이너 공유 폴더에 저장)
IG_SESSION_FILE = Path("/app/ig_session") / "session.json"

CRONJOBS = [ 
    # max 1 h sleep 후 업로드
    # 전날 22:00‒23:00 사이 → 다음날 아침 메뉴 업로드
    (
        '0 22 * * *',
        'meals.services.upload_breakfast',
        '>> /tmp/kshs_cron.log 2>&1'
    ),

    # 당일 8:00‒9:00 사이 → 점심 메뉴 업로드
    (
        '0 8 * * *',
        'meals.services.upload_lunch',
        '>> /tmp/kshs_cron.log 2>&1'
    ),

    # 당일 13:00‒14:00 사이 → 저녁 메뉴 업로드
    (
        '0 13 * * *',
        'meals.services.upload_dinner',
        '>> /tmp/kshs_cron.log 2>&1'
    ),
]