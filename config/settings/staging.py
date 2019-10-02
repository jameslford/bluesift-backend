import os
import dj_database_url
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

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True

REDIRECT_URL = 'https://www.bluesift-staging-frontend.herokuapp.com/'
DEFAULT_ADDRESS_INSTANCE = 1

PRODUCTION_DB_URL = os.environ['HEROKU_POSTGRESQL_WHITE_URL']

DATABASES = {
    'default': {},
    'scraper_default': {},
    'scraper_revised': {},
    'production': {}
}

DATABASES['default'] = dj_database_url.config(conn_max_age=500)
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
DATABASES['default']['OPTIONS'] = {'options': '-c search_path=default'}

DATABASES['scraper_default'] = dj_database_url.config(conn_max_age=500)
DATABASES['scraper_default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
DATABASES['scraper_default']['OPTIONS'] = {'options': '-c search_path=scraper_default'}

DATABASES['scraper_revised'] = dj_database_url.config(conn_max_age=500)
DATABASES['scraper_revised']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
DATABASES['scraper_revised']['OPTIONS'] = {'options': '-c search_path=scraper_revised'}


DATABASES['production'] = dj_database_url.config(default=PRODUCTION_DB_URL)
DATABASES['production']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

# WSGI_APPLICATION = 'config.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}


EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'BuildingBook'
EMAIL_HOST_PASSWORD = os.getenv('SMTP_PASSWORD')
DEFAULT_FROM_EMAIL = 'support@buildbooksite.herokuapp.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


GEOS_LIBRARY_PATH = os.getenv('GEOS_LIBRARY_PATH')
GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH')


def show_toolbar(request):
    # return request.user.is_staff
    return DEBUG


DEBUG_TOOLBAR_CONFIG = {
    # ...
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
    'config.custom_middleware.StagingMiddleware',
    'config.custom_middleware.LastSeenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
