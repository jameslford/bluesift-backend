import os
import dj_database_url
from corsheaders.defaults import default_headers
from .base import *



DEBUG = True
ENVIRONMENT = 'staging'
# BROKER_URL = 'PASS'
CELERY_BROKER_URL = os.environ['REDIS_URL']
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_RESULT_SERIALIZER = 'json'

STATIC_URL = '/static/'
SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = [
    'bluesift-staging-backend.herokuapp.com',
]
CORS_ORIGIN_WHITELIST = [
    'https://www.bluesift.com',
    'https://www.bluesift.com',
    'https://bluesift-staging-frontend.herokuapp.com'
    ]

CORS_ALLOW_HEADERS = list(default_headers) + [
    'Location',
    'sessionID'
]

CSRF_TRUSTED_ORIGINS = [
    'bluesift.com',
    'bluesift-staging-frontend.herokuapp.com',
    ]

REDIRECT_URL = 'https://www.bluesift-staging-frontend.herokuapp.com/'
DEFAULT_ADDRESS_INSTANCE = 1


DATABASES = {
    'default': {},
    'scraper_default': {},
    'scraper_revised': {},
}

DATABASES['default'] = dj_database_url.config(conn_max_age=500)
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
DATABASES['default']['OPTIONS'] = {'options': '-c search_path=default,public'}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    )
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ['REDIS_URL'],
        'TIMEOUT': 0,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "example"
    }
}



EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'BuildingBook'
EMAIL_HOST_PASSWORD = os.getenv('SMTP_PASSWORD')
DEFAULT_FROM_EMAIL = 'support@buildbooksite.herokuapp.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


GEOS_LIBRARY_PATH = os.getenv('GEOS_LIBRARY_PATH')
GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH')

SECRET_KEY = os.getenv('SECRET_KEY')
STAGING_DB_URI = os.getenv('STAGING_DB_URI')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
SCRAPER_AUTH_HEADER = os.getenv('SCRAPER_AUTH_HEADER')
LOCAL_DB_PASSWORD = os.getenv('LOCAL_DB_PASSWORD')


def show_toolbar(request):
    return DEBUG


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'config.settings.staging.show_toolbar',
}


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'config.custom_middleware.StagingMiddleware',
    # 'config.custom_middleware.LastSeenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
