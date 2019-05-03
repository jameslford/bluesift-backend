import os
import dj_database_url
from .base import *

DEBUG = True
ENVIRONMENT = 'staging'


STATIC_URL = '/static/'
SECRET_KEY = os.environ['SECRET_KEY']


ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True

REDIRECT_URL = 'https://www.bluesift-staging-frontend.herokuapp.com/'
DEFAULT_ADDRESS_INSTANCE = 1

AWS_STATIC_BUCKET_NAME = 'pixidesk-staging'
AWS_MEDIA_BUCKET_NAME = "pixidesk-staging-media"
AWS_S3_REGION_NAME = 'us-east-1'


DATABASES = {
    'default': {
        'ENGINE': '',
        'NAME': 'BBDB',
        'USER': 'postgres',
        'PASSWORD': '',
    },
    'production': {
        'ENGINE': '',
        'NAME': 'BBDB',
        'USER': 'postgres',
        'PASSWORD': '',
    }
}

PRODUCTION_DB_URL = os.environ['HEROKU_POSTGRESQL_WHITE_URL']

DATABASES['default'] = dj_database_url.config(conn_max_age=500)
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

DATABASES['production'] = dj_database_url.config(default=PRODUCTION_DB_URL)
DATABASES['production']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

# WSGI_APPLICATION = 'config.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'config.settings.custom_storage.StaticStorage'

MEDIAFILES_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'config.settings.custom_storage.MediaStorage'


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
    return True


DEBUG_TOOLBAR_CONFIG = {
    # ...
    'SHOW_TOOLBAR_CALLBACK': 'config.settings.staging.show_toolbar',
}


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
