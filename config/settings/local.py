from .base import *
from . passwords import *

DEBUG = True

STATIC_URL = '/static/'

DATA_PATH = os.getcwd() + '\\config\\management\\data\\*.txt'

ALLOWED_HOSTS = []

REDIRECT_URL = 'https://www.google.com/'
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'BuildingBook'
EMAIL_HOST_PASSWORD = 'M&5#OXp29yMX'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


AWS_STATIC_BUCKET_NAME = 'pixidesk-development'
AWS_MEDIA_BUCKET_NAME = 'pixidesk-development-media'
AWS_S3_REGION_NAME = 'us-east-1'



DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'PixiDesk',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
    }
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        #'rest_framework.authentication.BasicAuthentication',
        #'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}
# "C:\\OSGeo4W\\bin\\gdal202.dll"
# GDAL_LIBRARY_PATH = "C:\\OSGeo4W64\\bin\\"
GDAL_LIBRARY_PATH = 'C:\\OSGeo4W64\\bin\\gdal203.dll'
# GDAL_LIBRARY_PATH = "C:\\OSGeo4W\\bin\\gdal202.dll"
# GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH')
# GEOS_LIBRARY_PATH = os.getenv('GEOS_LIBRARY_PATH')