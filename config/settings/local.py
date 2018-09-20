from .base import *
from . passwords import *

DEBUG = True

STATIC_URL = '/static/'


ALLOWED_HOSTS = []

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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        #'rest_framework.authentication.BasicAuthentication',
        #'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}