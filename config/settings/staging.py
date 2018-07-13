from .base import *
import dj_database_url

DEBUG = True


STATIC_URL = '/static/'
SECRET_KEY = os.environ['SECRET_KEY']


ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'



AWS_STATIC_BUCKET_NAME = 'pixidesk-staging'
AWS_MEDIA_BUCKET_NAME = "pixidesk-staging-media"
AWS_S3_REGION_NAME =   'us-east-1'


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgresql_psycopg2',
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





