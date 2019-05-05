from .base import *
from .passwords import *

DEBUG = True
ENVIRONMENT = 'local'

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
            'options': '-c search_path=bluesift_default'
        },
        'NAME': 'buildbook',
        'USER': 'postgres',
        'PASSWORD': LOCAL_DB_PASSWORD,
    },
    'scraper_default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
            'options': '-c search_path=scraper_default'
            },
        'NAME': 'buildbook',
        'USER': 'postgres',
        'PASSWORD': LOCAL_DB_PASSWORD,
    },
    'scraper_revised': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
            'options': '-c search_path=scraper_revised'
            },
        'NAME': 'buildbook',
        'USER': 'postgres',
        'PASSWORD': LOCAL_DB_PASSWORD,
    }
}



REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1'
]


GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH')
GEOS_LIBRARY_PATH = os.getenv('GEOS_LIBRARY_PATH')
