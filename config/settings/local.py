from .base import *
from . passwords import *

DEBUG = True

STATIC_URL = '/static/'

CORS_ORIGIN_ALLOW_ALL = True

DATA_PATH = os.getcwd() + '\\config\\management\\data\\*.txt'
ZIP_PATH = os.getcwd() + '\\config\\management\\zips\\zipcodes.csv'

ALLOWED_HOSTS = ['*']

REDIRECT_URL = 'https://www.google.com/'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'BuildingBook'
EMAIL_HOST_PASSWORD = 'M&5#OXp29yMX'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'config.settings.custom_storage.StaticStorage'

MEDIAFILES_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'config.settings.custom_storage.MediaStorage'

# MEDIA_ROOT = os.path.join(BASE_DIR, 'management\\media')
# MEDIA_URL = 'management/media/'

AWS_STATIC_BUCKET_NAME = 'pixidesk-development'
AWS_MEDIA_BUCKET_NAME = 'pixidesk-development-media'
AWS_S3_REGION_NAME = 'us-east-1'


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'buildbook',
        'USER': 'postgres',
        'PASSWORD': '%&N2aBsub',
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


GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH')
GEOS_LIBRARY_PATH = os.getenv('GEOS_LIBRARY_PATH')

# DATA_PATH = os.getcwd() + '/config/management/data/production_data.csv'
DATA_PATH = os.getcwd() + '/config/management/data/final_list.csv'
ZIP_PATH = os.getcwd() + '/config/management/zips/zipcodes.csv'
