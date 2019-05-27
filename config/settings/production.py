import os
import dj_database_url
from .base import *

DEBUG = False
ENVIRONMENT = 'production'

STATIC_URL = '/static/'
SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REDIRECT_URL = 'https://www.bluesift.com/'
DEFAULT_ADDRESS_INSTANCE = 1

DATABASES = {
    'default': {},
}


DATABASES['default'] = dj_database_url.config(conn_max_age=500)
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

# WSGI_APPLICATION = 'config.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
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


def show_toolbar(request):
    # return request.user.is_staff
    return False


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'config.settings.production.show_toolbar',
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
