import dj_database_url
from celery.schedules import crontab
from .base import *
# from .passwords import *
from .passwords import *


DEBUG = True
ENVIRONMENT = 'local'

SECRET_KEY = SECRET_KEY

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_RESULT_SERIALIZER = 'json'

STATIC_URL = '/static/'

CORS_ORIGIN_ALLOW_ALL = True

ALLOWED_HOSTS = ['*']

REDIRECT_URL = 'https://www.google.com/'

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'BuildingBook'
EMAIL_HOST_PASSWORD = 'M&5#OXp29yMX'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


MEDIA_ROOT = os.path.join(BASE_DIR, 'management\\media')
MEDIA_URL = 'management/media/'


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'OPTIONS': {
            'options': '-c search_path=default,public'
        },
        'NAME': 'buildbook',
        'USER': 'postgres',
        'PASSWORD': LOCAL_DB_PASSWORD,
        'TEST': {
            'NAME': 'test_default'
        }
    },
    'scraper_default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
            'options': '-c search_path=scraper_default,public'
            },
        'NAME': 'buildbook',
        'USER': 'postgres',
        'PASSWORD': LOCAL_DB_PASSWORD,
        'TEST': {
            'NAME': 'test_scraper_default'
        }
    },
    'scraper_revised': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
            'options': '-c search_path=scraper_revised,public'
            },
        'NAME': 'buildbook',
        'USER': 'postgres',
        'PASSWORD': LOCAL_DB_PASSWORD,
        'TEST': {
            'NAME': 'test_scraper_revised'
        }
    },
}

DATABASES['staging_scraper_default'] = dj_database_url.config(default=STAGING_DB_URI)
DATABASES['staging_scraper_default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
DATABASES['staging_scraper_default']['OPTIONS'] = {'options': '-c search_path=scraper_default'}
DATABASES['staging_scraper_revised'] = dj_database_url.config(default=STAGING_DB_URI)
DATABASES['staging_scraper_revised']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
DATABASES['staging_scraper_revised']['OPTIONS'] = {'options': '-c search_path=scraper_revised'}


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'config.custom_middleware.StagingMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]


REST_FRAMEWORK = {
    # 'DEFAULT_RENDERER_CLASSES': [
    #     'rest_framework.renderers.JSONRenderer',
    #     'rest_framework.renderers.BrowsableAPIRenderer'
    # ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}


INTERNAL_IPS = [
    '127.0.0.1'
]
