import os
import dj_database_url
from corsheaders.defaults import default_headers
from .base import *

DEBUG = False
ENVIRONMENT = 'production'
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
    'bluesift-production-backend.herokuapp.com'
    ]
CORS_ORIGIN_WHITELIST = [
    'https://www.bluesift.com',
]
CORS_ALLOW_HEADERS = list(default_headers) + [
    'Location',
    'SessionID'
]
CSRF_TRUSTED_ORIGINS = [
    'bluesift.com',
    'bluesift-staging-frontend.herokuapp.com',
    'bluesift.com/',
    ]


REDIRECT_URL = 'https://www.bluesift.com/'
DEFAULT_ADDRESS_INSTANCE = 1

STAGING_DB_URL = os.environ['STAGING_DB_URL']

DATABASES = {
    'default': {},
    'staging': {}
}


DATABASES['default'] = dj_database_url.config(conn_max_age=500)
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
# DATABASES['default']['OPTIONS'] = {'options': '-c search_path=default'}
DATABASES['staging'] = dj_database_url.config(STAGING_DB_URL)
DATABASES['staging']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
DATABASES['staging']['OPTIONS'] = {'options': '-c search_path=default,postgis'}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}


EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'BlueSift'
EMAIL_HOST_PASSWORD = os.getenv('SMTP_PASSWORD')
DEFAULT_FROM_EMAIL = 'support@Bluesift.com'
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
    return False


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'config.settings.production.show_toolbar',
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'config.custom_middleware.LastSeenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
