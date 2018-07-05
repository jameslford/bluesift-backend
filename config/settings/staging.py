from .base import *
import dj_database_url

DEBUG = True


STATIC_URL = '/static/'
SECRET_KEY = os.environ['SECRET_KEY']


ALLOWED_HOSTS = ['*']
#CORS_ORIGIN_ALLOW_ALL = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'



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



'''EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'jameslford8@gmail.com'
EMAIL_HOST_PASSWORD = '%&N2aBsub'
EMAIL_PORT = 587'''





''' <!-- Staging policy -->
<CORSConfiguration>
	<CORSRule>
		<AllowedOrigin>*</AllowedOrigin>
		<AllowedMethod>GET</AllowedMethod>
		<MaxAgeSeconds>3000</MaxAgeSeconds>
		<AllowedHeader>Authorization</AllowedHeader>
	</CORSRule>
</CORSConfiguration> 

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::111696298610:user/pixidesk-staging"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::pixidesk-staging/*"
        }
    ]
}

'''


''' <?xml version="1.0" encoding="UTF-8"?>
<CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
<CORSRule>
    <AllowedOrigin>*</AllowedOrigin>
    <AllowedMethod>PUT</AllowedMethod>
    <AllowedMethod>POST</AllowedMethod>
    <AllowedMethod>GET</AllowedMethod>
    <MaxAgeSeconds>3000</MaxAgeSeconds>
    <AllowedHeader>*</AllowedHeader>
</CORSRule>
</CORSConfiguration>


{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::111696298610:user/pixidesk-development"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::pixidesk-development/*"
        }
    ]
}


'''