from .base import *
import dj_database_url

DEBUG = True
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = ['*']

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgresql_psycopg2',
        'NAME': 'BBDB',
        'USER': 'postgres',
        'PASSWORD': '',
    }
}


DATABASES['default'] = dj_database_url.config(conn_max_age=500)


AWS_STATIC_BUCKET_NAME = 'pixidesk-staging'
AWS_MEDIA_BUCKET_NAME = "pixidesk-staging-media"
AWS_S3_REGION_NAME =   'us-east-1'

#WSGI_APPLICATION = 'config.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
       # 'rest_framework.authentication.BasicAuthentication',
       # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}



EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'jameslford8@gmail.com'
EMAIL_HOST_PASSWORD = '%&N2aBsub'
EMAIL_PORT = 587