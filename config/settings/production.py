import os
import dj_database_url
from .base import *

DEBUG = False


STATIC_URL = '/static/'
SECRET_KEY = os.environ['SECRET_KEY']


ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REDIRECT_URL = 'https://www.google.com/'
DEFAULT_ADDRESS_INSTANCE = 1

AWS_STATIC_BUCKET_NAME = 'pixidesk-production'
AWS_MEDIA_BUCKET_NAME = "pixidesk-production-media"
AWS_S3_REGION_NAME = 'us-east-1'


DATABASES = {
    'default': {
        'ENGINE': '',
        'NAME': 'BBDB',
        'USER': 'postgres',
        'PASSWORD': '',
    }
}


DATABASES['default'] = dj_database_url.config(conn_max_age=500)
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'





#WSGI_APPLICATION = 'config.wsgi.application'

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
EMAIL_HOST_PASSWORD = 'M&5#OXp29yMX'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DATA_PATH = PRODUCTION_DATA_WRITE_PATH
ZIP_PATH = os.getcwd() + '/config/management/zips/zipcodes.csv'

GEOS_LIBRARY_PATH = os.getenv('GEOS_LIBRARY_PATH')
GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH')

# GEOS_LIBRARY_PATH = '/app/.heroku/vendor/lib/libgeos_c.so'
# GDAL_LIBRARY_PATH = '/app/.heroku/vendor/lib/libgdal.so'

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


# 'GDAL_LIBRAY_PATH' '/app/.heroku/vendor/lib/libgdal.so'
# 'GEOS_LIBRARY_PATH' '/app/.heroku/vendor/lib/libgeos_c.so'


# AWS_ACCESS_KEY_ID :    AKIAJMXZBZGT7YLT2QCA
# AWS_SECRET_ACCESS_KEY : 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
# BUILD_WITH_GEO_LIBRARIES : 1
# DATABASE_URL : postgres://jhawnscgwbzplm:8229cdbbf4e81a3b3875131f3ca2912b11b441eb90690e357c95f0ed9fb37b56@ec2-54-225-237-84.compute-1.amazonaws.com:5432/de1p8mp8pa6hj5
# DISABLE_COLLECTSTATIC : 1
# DJANGO_SETTINGS_MODULE : config.settings.production
# GDAL_LIBRAY_PATH : /app/.heroku/vendor/lib/libgdal.so
# GEOS_LIBRARY_PATH : /app/.heroku/vendor/lib/libgeos_c.so
# SECRET_KEY : 7_gs57^=4i^3l74e=(*ko2m4&-ws82o3akofa6$+26a)sqqxa4

# postgres://mzfomutrqqlhaj:dcef1fb2409b78a68ad4639da3d8be531aa0cc86d151f500ba440bd464fe710e@ec2-54-235-159-101.compute-1.amazonaws.com:5432/dl7aa1f30f3b8