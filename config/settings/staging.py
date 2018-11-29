import os
import dj_database_url
from .base import *

DEBUG = True


STATIC_URL = '/static/'
SECRET_KEY = os.environ['SECRET_KEY']


ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REDIRECT_URL = 'https://www.google.com/'
DEFAULT_ADDRESS_INSTANCE = 1

AWS_STATIC_BUCKET_NAME = 'pixidesk-staging'
AWS_MEDIA_BUCKET_NAME = "pixidesk-staging-media"
AWS_S3_REGION_NAME = 'us-east-1'


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'BBDB',
        'USER': 'postgres',
        'PASSWORD': '',
    }
}


DATABASES['default'] = dj_database_url.config(conn_max_age=500)




#WSGI_APPLICATION = 'config.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}



EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'BuildingBook'
EMAIL_HOST_PASSWORD = 'M&5#OXp29yMX'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DATA_PATH = os.getcwd() + '/config/management/data/*.txt'

GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH')
GEOS_LIBRARY_PATH = os.getenv('GEOS_LIBRARY_PATH')
