from .base import *
from . passwords import *

DEBUG = True

STATIC_URL = '/static/'

CORS_ORIGIN_ALLOW_ALL = True

DATA_PATH = os.getcwd() + '\\config\\management\\data\\*.txt'
ZIP_PATH = os.getcwd() + '\\config\\management\\zips\\zipcodes.csv'

ALLOWED_HOSTS = ['*']

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
        'NAME': 'buildbook',
        'USER': 'postgres',
        'PASSWORD': '%&N2aBsub',
    }
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        #'rest_framework.authentication.BasicAuthentication',
        #'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

# "C:\Users\james\Documents\Code\BuildingBook\envs\env\GDAL-2.3.2-cp36-cp36m-win_amd64.whl"

# "C:\\OSGeo4W\\bin\\gdal202.dll"
# GDAL_LIBRARY_PATH = ";C:\\OSGeo4W64\\bin\\"
# GDAL_LIBRARY_PATH = "C\\Users\\james\\Documents\\Code\\BuildingBook\\envs\\env\\Lib\\site-packages\\osgeo\\data\\gdal"
# GEOS_LIBRARY_PATH = 'C:\\OSGeo4W64\\bin\\geos.dll'
# GDAL_LIBRARY_PATH = "C:\\Program Files\\GDAL\\gdal203.dll"
# GEOS_LIBRARY_PATH = ";C:\\Program Fi1les\\GDAL\\geos.dll"
# GDAL_LIBRARY_PATH = "C:\\OSGeo4W\\bin\\gdal202.dll"
GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH')
GEOS_LIBRARY_PATH = os.getenv('GEOS_LIBRARY_PATH')

DATA_PATH = os.getcwd() + '/config/management/data/*.txt'
ZIP_PATH =  os.getcwd() + '/config/management/zips/zipcodes.csv'
