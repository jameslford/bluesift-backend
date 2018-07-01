from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


AWS_STATIC_BUCKET_NAME = 'pixidesk-staging'
AWS_MEDIA_BUCKET_NAME = "pixidesk-staging-media"
AWS_S3_REGION_NAME =   'us-east-1'



REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}


EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'jameslford8@gmail.com'
EMAIL_HOST_PASSWORD = '%&N2aBsub'
EMAIL_PORT = 587